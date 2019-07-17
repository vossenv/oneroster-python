import json
import logging
import requests
from .util import *

class CleverConnector():

    def __init__(self, options):

        self.logger = logging.getLogger("clever")
        self.client_id = options.get('client_id')
        self.client_secret = options.get('client_secret')
        self.max_users = options.get('max_user_count') or 0
        self.match_groups_by = options.get('match_groups_by') or 'name'
        self.page_size = options.get('page_size') or 10000
        self.access_token = options.get('access_token')
        self.host = options.get('host') or 'https://api.clever.com/v2.1/'
        self.user_count = 0
        self.calls_made = []

        if not self.access_token:
            self.authenticate()

        self.auth_header = {
            "Authorization": "Bearer " + self.access_token}

    def authenticate(self):
        try:
            auth_resp = requests.get("https://clever.com/oauth/tokens", auth=(self.client_id, self.client_secret))
            self.access_token = json.loads(auth_resp.content)['data'][0]['access_token']
        except ValueError:
            raise LookupError("Authorization attempt failed...")

    def get_users(self,
                  group_filter=None,  # Type of group (class, course, school)
                  group_name=None,  # Plain group name (Math 6)
                  user_filter=None,  # Which users: users, students, staff
                  ):

        results = []
        calls = self.translate(group_filter=group_filter, user_filter=user_filter)
        if group_filter == 'courses':
            results = self.get_users_for_course(name=group_name, user_filter=user_filter)
        elif group_filter:
            for c in calls:
                keylist = self.get_primary_key(group_filter, group_name)
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

        #self.logger.info("Collected " + str(self.user_count) + " total users for calls:" + str(self.calls_made))
        self.calls_made = []
        self.user_count = 0
        return results[0:self.max_users] if self.max_users > 0 else results


    def get_all_users(self, calls):
        return [self.make_call(c) for c in calls]

    def make_call(self, url):
        next = ""
        collected_objects = []
        count_users = '/users' in url or '/students' in url or '/teachers' in url
        if count_users:
            self.logger.info("Getting users from: " + url)
        while True:
            if self.max_users and self.user_count > self.max_users:
                break
            try:
                response = requests.get(url + '?limit=' + str(self.page_size) + next, headers=self.auth_header)
                new_objects = json.loads(response.content)['data']
                if new_objects:
                    collected_objects.extend(new_objects)
                    next = '&starting_after=' + new_objects[-1]['data']['id']
                    if count_users:
                        self.user_count += len(new_objects)
                        self.logger.info("Collected users: " + str(self.user_count))
                else:
                    break
            except Exception as e:
                raise e
        extracted_objects = [o['data'] for o in collected_objects]
        return extracted_objects

    def get_primary_key(self, type, name):
        if self.match_groups_by == 'id':
            return [name]
        if self.max_users > 0  and self.user_count > self.max_users:
            return []

        url = self.translate(None, type)[0]
        objects = self.make_call(url)
        id_list = []

        for o in objects:
            try:
                if decode_string(o[self.match_groups_by]) == decode_string(name):
                    id_list.append(o['id'])
            except KeyError:
                self.logger.warning("No property: '" + self.match_groups_by +
                                    "' was found on " + type.rstrip('s') + " for entity '" + name + "'")
                break
        if not id_list:
            self.logger.warning("No objects found for " + type + ": '" + name + "'")
        return id_list

    def get_sections_for_course(self, name):
        id_list = self.get_primary_key('courses', name)
        sections = []
        for i in id_list:
            call = self.translate('courses', 'sections')[0].format(i)
            sections.extend(self.make_call(call))
        if not sections:
            self.logger.warning("No sections found for course '" + name + "'")
            return []
        else:
            return [s['id'] for s in sections]

    def get_users_for_course(self, name, user_filter='users'):
        urls = self.translate('sections', user_filter)
        sections = self.get_sections_for_course(name)
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
            raise ValueError("Unrecognized method request: 'get_" + user_filter + "_for_" + group_filter + "'")

        group_filter = group_filter + "/{}/" if group_filter else ''
        url = self.host + group_filter + user_filter

        if user_filter == 'users':
            return [url.replace(user_filter, 'students'), url.replace(user_filter, 'teachers')]
        else:
            return [url]
