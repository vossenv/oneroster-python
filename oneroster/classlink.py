import base64
import collections
import hashlib
import hmac
import json
import logging
import time
from random import randint

import requests
from six.moves import urllib

from .util import *


class ClasslinkConnector():
    """ Starts connection and makes queries with One-Roster API"""

    def __init__(self, options):
        self.logger = logging.getLogger("classlink")
        self.host_name = options.get('host')
        self.client_id = options.get('client_id')
        self.client_secret = options.get('client_secret')
        self.key_identifier = options.get('key_identifier')
        self.max_users = options.get('max_user_count') or 0
        self.page_size = options.get('page_size') or 10000
        self.user_count = 0
        self.classlink_api = ClasslinkAPI(self.client_id, self.client_secret)
        self.match_groups_by = options.get('match_groups_by') or 'name'
        self.page_size = self.page_size if self.page_size > 0 else 10000

        self.logger.setLevel(logging.DEBUG)
        self.logger.info("Initializing connector with options: ")
        self.logger.info(filter_dict(vars(self), ['client_secret']))

    def get_users(self,
                  group_filter=None,  # Type of group (class, course, school)
                  group_name=None,  # Plain group name (Math 6)
                  user_filter=None,  # Which users: users, students, staff
                  match_on=None,
                  ):

        results = []
        self.check_filters(group_filter, user_filter)
        match_on = self.match_groups_by if not match_on else match_on

        log_group_details(user_filter, group_filter, group_name, self.logger)
        if group_filter == 'courses':
            list_classes = []
            id_list = self.execute_actions('courses', group_name, self.key_identifier, 'key_identifier', match_on)
            for k in id_list:
                list_classes.extend(self.execute_actions(group_filter, user_filter, k, 'course_classlist', match_on))
            for c in list_classes:
                results.extend(self.execute_actions('classes', user_filter, c, 'mapped_users', match_on))
        elif group_filter:
            id_list = self.execute_actions(group_filter, None, group_name, 'key_identifier', match_on)
            for k in id_list:
                results.extend(self.execute_actions(group_filter, user_filter, k, 'mapped_users', match_on))
        else:
            results.extend(self.execute_actions(None, user_filter, None, 'all_users', match_on))

        if not results:
            log_bad_matcher_warning(group_filter, group_name, match_on)
        return results[0:self.max_users] if self.max_users > 0 else results

    def execute_actions(self, group_filter, user_filter, identifier, request_type, match_on):
        if request_type == 'all_users':
            url_request = self.construct_url(user_filter, None, '', None)
            result = self.make_call(url_request, 'all_users', None, match_on)
        elif request_type == 'key_identifier':
            if group_filter == 'courses':
                url_request = self.construct_url(user_filter, identifier, 'course_classlist', None)
                result = self.make_call(url_request, 'key_identifier', group_filter, user_filter, match_on)
            else:
                url_request = self.construct_url(group_filter, identifier, 'key_identifier', None)
                result = self.make_call(url_request, 'key_identifier', group_filter, identifier, match_on)

        elif request_type == 'mapped_users':
            base_filter = group_filter if group_filter == 'schools' else 'classes'
            url_request = self.construct_url(base_filter, identifier, request_type, user_filter)
            result = self.make_call(url_request, 'mapped_users', group_filter, group_filter, match_on)
        elif request_type == 'course_classlist':
            url_request = self.construct_url("", identifier, 'users_from_course', None)
            result = self.make_call(url_request, request_type, group_filter, match_on)
        return result

    def construct_url(self, base_string_seeking, id_specified, request_type, users_filter):
        if request_type == 'course_classlist':
            url_ender = 'courses/?limit=' + str(self.page_size) + '&offset=0'
        elif request_type == 'users_from_course':
            url_ender = 'courses/' + id_specified + '/classes?limit=' + str(self.page_size) + '&offset=0'
        elif users_filter is not None:
            url_ender = base_string_seeking + '/' + id_specified + '/' + users_filter + '?limit=' + str(self.page_size) + '&offset=0'
        else:
            url_ender = base_string_seeking + '?limit=' + str(self.page_size) + '&offset=0'
        return self.host_name + url_ender

    def get_url(self, url):
        try:
            response = self.classlink_api.make_roster_request(url)
        except Exception as e:
            raise e.__class__(log_failed_call(e))
        if not isinstance(response, requests.Response):
            raise requests.RequestException("404 No response recieved: " + url)
        elif response.status_code is not 200:
            raise requests.RequestException(log_bad_response(response.status_code, response.content))
        try:
            next = response.links.get('next')
            next_url = next['url'] if next else None
            full_data = json.loads(response.content)
            return list(full_data.values())[0], next_url
        except TypeError as e:
            raise requests.RequestException(log_bad_json(e, response.content))

    def make_call(self, url, request_type, group_filter, group_name=None, match_on=None):
        object_list = []
        next_url = url
        count_users = '/users' in url or '/students' in url or '/teachers' in url
        if count_users:
            log_call_details(url, self.logger)
        while next_url:
            data, next_url = self.get_url(next_url)
            if request_type == 'key_identifier':
                for entry in data:
                    if match_object(entry, match_on, group_name):
                        try:
                            object_list.append(entry[self.key_identifier])
                        except KeyError:
                            raise KeyError(log_bad_key_id(self.key_identifier))
                if not next_url and not object_list:
                    self.logger.warning(log_bad_matcher_warning(group_filter, group_name, match_on))
            elif request_type == 'course_classlist':
                object_list.extend([x[self.key_identifier] for x in data])
            else:
                object_list.extend(data)

            if count_users:
                log_followup_details(len(object_list), self.logger)
                self.user_count += len(data)
            if self.max_users and self.user_count >= self.max_users:
                break

        if not object_list and not self.max_users:
            self.logger.warning(log_bad_matcher_warning(group_filter, group_name, match_on))
        return object_list

    def check_filters(self, group_filter, user_filter):

        group_filter = group_filter if group_filter else ''
        user_filter = user_filter if user_filter else ''

        allowed_calls = [
            'classes_students',
            'classes_teachers',
            'classes_users',

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
            '_classes',
            '_courses',
            '_schools',
        ]

        if group_filter + "_" + user_filter not in allowed_calls:
            raise ValueError("Unrecognized request: 'get_" + user_filter + "_for_" + group_filter + "'")


##### Below code from classlink repository.  TB removed at a later date.

class ClasslinkAPI(object):
    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret

    def make_roster_request(self, url):

        """
        make a request to a given url with the stored key and secret
        :param url:     The url for the request
        :return:        A dictionary containing the status_code and response
        """

        # Generate timestamp and nonce
        timestamp = str(int(time.time()))
        nonce = self.__generate_nonce(len(timestamp))

        # Define oauth params
        oauth = {
            'oauth_consumer_key': self._client_id,
            'oauth_signature_method': 'HMAC-SHA256',
            'oauth_timestamp': timestamp,
            'oauth_nonce': nonce
        }

        # Split the url into base url and params
        url_pieces = url.split("?")
        url_params = {}

        # Add the url params if they exist
        if len(url_pieces) == 2:
            url_params = self.__paramsToDict(url_pieces[1])
            all_params = self.__merge_dicts(oauth, url_params)
        else:
            all_params = oauth.copy()

        # Generate the auth signature
        base_info = self.__build_base_string(url_pieces[0], 'GET', all_params)
        composite_key = urllib.parse.quote_plus(self._client_secret) + "&"
        auth_signature = self.__generate_auth_signature(base_info, composite_key)
        oauth["oauth_signature"] = auth_signature

        # Generate the auth header
        auth_header = self.__build_auth_header(oauth)

        return self.__make_get_request(url_pieces[0], auth_header, url_params)

    def __merge_dicts(self, oauth, params):
        """
        Merge the oauth and param dictionaries
        :param oauth:       The oauth params
        :param params:      The url params
        :return:            A merged dictionary
        """
        result = oauth.copy()
        result.update(params)
        return result

    def __generate_nonce(self, nonce_len):
        """
        Generate a random nonce
        :param nonce_len:   Length of the nonce
        :return:            The nonce
        """
        characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        result = ""
        for i in range(0, nonce_len):
            result += characters[randint(0, len(characters) - 1)]

        return result

    def __paramsToDict(self, url_params):
        """
        Convert the url params to a dict
        :param url_params:      The url params
        :return:                A dictionary of the url params
        """
        params = url_params.split("&")
        result = {}
        for value in params:
            value = urllib.parse.unquote(value)
            split = value.split("=")
            if len(split) == 2:
                result[split[0]] = split[1]
            else:
                result["filter"] = value[7:]
        return result

    def __build_base_string(self, baseurl, method, all_params):
        """
        Generate the base string for the generation of the oauth signature
        :param baseurl:     The base url
        :param method:      The HTTP method
        :param all_params:  The url and oauth params
        :return:            The base string for the generation of the oauth signature
        """
        result = []
        params = collections.OrderedDict(sorted(all_params.items()))
        for key, value in params.items():
            result.append(key + "=" + urllib.parse.quote(value))
        return method + "&" + urllib.parse.quote_plus(baseurl) + "&" + urllib.parse.quote_plus("&".join(result))

    def __generate_auth_signature(self, base_info, composite_key):
        """
        Generate the oauth signature
        :param base_info:       The base string generated from method, url, and params
        :param composite_key:   The componsite key of secret and &
        :return:                The oauth signature
        """
        digest = hmac.new(str.encode(composite_key), msg=str.encode(base_info), digestmod=hashlib.sha256).digest()
        return base64.b64encode(digest).decode()

    def __build_auth_header(self, oauth):
        """
        Generates the oauth header from the oauth params
        :param oauth:   The oauth params
        :return:        The oauth header for the request
        """
        result = "OAuth "
        values = []
        for key, value in oauth.items():
            values.append(key + "=\"" + urllib.parse.quote_plus(value) + "\"")

        result += ",".join(values)
        return result

    def __make_get_request(self, url, auth_header, url_params):
        """
        Make the get request
        :param url:             The base url of the request
        :param auth_header:     The auth header
        :param url_params:      The params from the url
        :return:                A dictionary of the status_code and response
        """

        try:
            return requests.get(url=url, headers={"Authorization": auth_header}, params=url_params)

        except Exception as e:
            return {"status_code": 0, "response": "An error occurred, check your URL"}
