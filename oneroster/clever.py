import json
import logging

import requests

from .util import *


class CleverConnector():

    def __init__(self,
                 host='https://api.clever.com/v2.1/',
                 access_token=None,
                 key_identifier='id',
                 match_on=None,
                 max_users=0,
                 page_size=10000,
                 **kwargs
                 ):


        self.logger = logging.getLogger("clever")
        self.max_users = max_users
        self.match_groups_by = match_on if match_on else ['name', 'id']
        self.page_size = page_size
        self.access_token = access_token
        self.host = host
        self.user_count = 0
        self.key_identifier = key_identifier
        self.page_size = self.page_size if self.page_size > 0 else 10000
        self.logger.debug("Initializing connector with options: ")
        self.logger.debug(filter_dict(vars(self), ['access_token']))



    def get_users(self,
                  group_filter=None,  # Type of group (class, course, school)
                  group_name=None,  # Plain group name (Math 6)
                  user_filter=None,  # Which users: users, students, staff
                  match_on=None,
                  ):

        if not self.access_token:
            raise AssertionError("Clever requires an access token but none was provided")

        match_on = self.match_groups_by if not match_on else match_on
        calls = self.translate(group_filter=group_filter, user_filter=user_filter)
        log_group_details(user_filter, group_filter, group_name, self.logger)

        results = []
        self.user_count = 0
        if group_filter == 'courses':
            results = self.get_users_for_course(name=group_name, user_filter=user_filter)
        elif group_filter:
            for c in calls:
                keylist = self.get_primary_key(group_filter, group_name, match_on)
                if not keylist:
                    break

                for i in keylist:
                    results.extend(self.make_call(c.format(i)))
        else:
            # All users
            [results.extend(self.make_call(c)) for c in calls]

        for user in results:
            user['givenName'] = user['name'].get('first')
            user['familyName'] = user['name'].get('last')
            user['middleName'] = user['name'].get('middle')

        return results[0:self.max_users] if self.max_users > 0 else results

    def get_all_users(self, calls):
        return [self.make_call(c) for c in calls]

    def make_call(self, url):
        next = ""
        collected_objects = []
        count_users = '/users' in url or '/students' in url or '/teachers' in url
        if count_users:
            log_call_details(url, self.logger)
        while True:
            if self.max_users and self.user_count > self.max_users:
                break

            try:
                header = {"Authorization": "Bearer " + self.access_token}
                response = requests.get(url + '?limit=' + str(self.page_size) + next, headers=header)
            except Exception as e:
                raise e.__class__(log_failed_call(e))
            if response.status_code is not 200:
                raise requests.RequestException(log_bad_response(response.status_code, response.content))
            try:
                new_objects = json.loads(response.content)['data']
            except TypeError as e:
                raise requests.RequestException(log_bad_json(e, response.content))

            if new_objects:
                collected_objects.extend(new_objects)
                try:
                    next = '&starting_after=' + new_objects[-1]['data'][self.key_identifier]
                except KeyError:
                    raise AttributeError(log_bad_key_id(self.key_identifier))
                if count_users:
                    self.user_count += len(new_objects)
                    log_followup_details(len(new_objects), self.logger)
            else:
                break
        extracted_objects = [o['data'] for o in collected_objects]
        return extracted_objects

    def get_primary_key(self, type, name, match_on=None):
        match_on = self.match_groups_by if not match_on else match_on
        if self.match_groups_by == 'id':
            return [name]
        if self.max_users > 0 and self.user_count > self.max_users:
            return []

        url = self.translate(None, type)[0]
        objects = self.make_call(url)
        id_list = []

        for o in objects:

            try:
                if match_object(o, match_on, name):
                    id_list.append(o[self.key_identifier])
            except Exception as e:
                self.logger.warning(e)
                break

        if not id_list:
            self.logger.warning(log_bad_matcher_warning(type, name, match_on))
        return id_list

    def get_sections_for_course(self, name, match_on=None):
        match_on = self.match_groups_by if not match_on else match_on
        id_list = self.get_primary_key('courses', name, match_on)
        sections = []
        for i in id_list:
            call = self.translate('courses', 'sections')[0].format(i)
            sections.extend(self.make_call(call))
        if not sections:
            self.logger.warning("No sections found for course '" + name + "'")
            return []
        else:
            return [s[self.key_identifier] for s in sections]

    def get_users_for_course(self, name, user_filter='users', match_on=None):
        match_on = self.match_groups_by if not match_on else match_on
        urls = self.translate('sections', user_filter)
        sections = self.get_sections_for_course(name, match_on)
        user_list = []
        for s in sections:
            for c in urls:
                user_list.extend(self.make_call(c.format(s)))
        if not user_list:
            self.logger.warning("No users found for course '" + name + "'")
        return user_list

    def translate(self, group_filter, user_filter):

        group_filter = group_filter if group_filter else ''
        user_filter = user_filter if user_filter else ''

        allowed_calls = [
            'sections_students',
            'sections_teachers',
            'sections_users',

            'courses_students',
            'courses_teachers',
            'courses_users',
            'courses_sections',

            'schools_students',
            'schools_teachers',
            'schools_users',

            '_students',
            '_teachers',
            '_users',
            '_sections',
            '_courses',
            '_schools',
        ]

        if group_filter + "_" + user_filter not in allowed_calls:
            raise ValueError("Unrecognized request: 'get_" + user_filter + "_for_" + group_filter + "'")

        group_filter = group_filter + "/{}/" if group_filter else ''
        url = self.host + group_filter + user_filter

        if user_filter == 'users':
            return [url.replace(user_filter, 'students'), url.replace(user_filter, 'teachers')]
        else:
            return [url]
