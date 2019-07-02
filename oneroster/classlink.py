import collections
import time
from random import randint
from six.moves import urllib
import hmac
import base64
import hashlib
import requests
import json
import logging
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
        self.page_size = str(options.get('page_size'))
        self.user_count = 0
        self.classlink_api = ClasslinkAPI(self.client_id, self.client_secret)
        self.match_groups_by = options.get('match_groups_by') or 'name'

    def get_users(self,
                  group_filter=None,  # Type of group (class, course, school)
                  group_name=None,  # Plain group name (Math 6)
                  user_filter=None,  # Which users: users, students, staff
                  ):

        results = []
        if group_filter == 'courses':
            key_id = self.execute_actions('courses', group_name, self.key_identifier, 'key_identifier')
            if key_id is None:
                return results
            list_classes = self.execute_actions(group_filter, user_filter, key_id, 'course_classlist')
            for each_class in list_classes:
                results.extend(self.execute_actions('classes', user_filter, each_class, 'mapped_users'))
        elif not group_filter:
            results.extend(self.execute_actions(None, user_filter, None, 'all_users'))
        else:
            key_id = self.execute_actions(group_filter, None, group_name, 'key_identifier')
            if key_id is None:
                return results
            returned_users = self.execute_actions(group_filter, user_filter, key_id, 'mapped_users')
            if returned_users is None:
                self.logger.warning("No users found for " + group_filter + "::" + group_name + "::" + user_filter)
                return results
            results.extend(returned_users)
        return results[0:self.max_users] if self.max_users > 0 else results

    def execute_actions(self, group_filter, user_filter, identifier, request_type):
        result = []
        if request_type == 'all_users':
            url_request = self.construct_url(user_filter, None, '', None)
            result = self.make_call(url_request, 'all_users', None)
        elif request_type == 'key_identifier':
            if group_filter == 'courses':
                url_request = self.construct_url(user_filter, identifier, 'course_classlist', None)
                result = self.make_call(url_request, 'key_identifier', group_filter, user_filter)
            else:
                url_request = self.construct_url(group_filter, identifier, 'key_identifier', None)
                result = self.make_call(url_request, 'key_identifier', group_filter, identifier)
        elif request_type == 'mapped_users':
            base_filter = group_filter if group_filter == 'schools' else 'classes'
            url_request = self.construct_url(base_filter, identifier, request_type, user_filter)
            result = self.make_call(url_request, 'mapped_users', group_filter, group_filter)
        elif request_type == 'course_classlist':
            url_request = self.construct_url("", identifier, 'users_from_course', None)
            result = self.make_call(url_request, request_type, group_filter)
        return result

    def construct_url(self, base_string_seeking, id_specified, request_type, users_filter):
        if request_type == 'course_classlist':
            url_ender = 'courses/?limit=' + self.page_size + '&offset=0'
        elif request_type == 'users_from_course':
            url_ender = 'courses/' + id_specified + '/classes?limit=' + self.page_size + '&offset=0'
        elif users_filter is not None:
            url_ender = base_string_seeking + '/' + id_specified + '/' + users_filter + '?limit=' + self.page_size + '&offset=0'
        else:
            url_ender = base_string_seeking + '?limit=' + self.page_size + '&offset=0'
        return self.host_name + url_ender

    def make_call(self, url, request_type, group_filter, group_name=None):
        user_list = []
        key = 'first'
        count_users = '/users' in url or '/students' in url or '/teachers' in url
        while key is not None:
            if self.max_users and self.user_count > self.max_users:
                break
            if key == 'first':
                response = self.classlink_api.make_roster_request(url)
            else:
                response = self.classlink_api.make_roster_request(response.links[key]['url'])
            if not response.ok:
                self.bad_response_handler(response)
                return
            if request_type == 'key_identifier':
                other = 'course' if group_filter == 'courses' else 'classes'
                name_identifier, revised_key = ('name', 'orgs') if group_filter == 'schools' else ('title', other)
                if self.match_groups_by is not 'name':
                    name_identifier = self.match_groups_by
                for entry in json.loads(response.content).get(revised_key):
                    if name_identifier not in entry:
                        self.logger.warning("match_groups_by attribute  '" + name_identifier + "'  not found for " + group_filter + " " + group_name +
                                            " ..... available keys are " + str(list(entry.keys())))
                        return
                    if decode_string(entry[name_identifier]) == decode_string(group_name):
                        try:
                            return entry[self.key_identifier]
                        except KeyError:
                            raise KeyError('Key identifier: ' + self.key_identifier + ' not a valid identifier')
                self.logger.warning("No match for '" + group_filter + " group name:" + group_name + "' found, using match_groups_by attribute '" + self.match_groups_by + "'")
                return
            elif request_type == 'course_classlist':
                for ignore, entry in json.loads(response.content).items():
                    user_list.append(entry[0][self.key_identifier])
            else:
                for ignore, users in json.loads(response.content).items():
                    user_list.extend(users)
            if key == 'last' or int(response.headers._store['x-count'][1]) < int(self.page_size):
                break
            key = 'next' if 'next' in response.links else 'last'
            self.user_count += len(user_list) if count_users else 0

        if not user_list and not self.max_users:
            self.logger.warning("No " + request_type + " for " + group_filter + "  " + group_name)

        return user_list

    def bad_response_handler(self, response):
        if response.reason == "Unauthorized":
            self.logger.warning(response.reason + " Invalid credentials used... ")
        elif response.reason == 'Not Found':
            self.logger.warning(response.reason + " .....Resource not found at " + response.text)
        else:
            self.logger.warning("Unexpected error, please review configuration")


class ClasslinkAPI(object):
    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret

    def hello(self):
        print("CLASSLINK")

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
