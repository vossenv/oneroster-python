import collections
import re

import mock
import pytest
from requests import Response

from oneroster.clever import *


@pytest.fixture()
def clever_api():
    options = {
        'host': 'https://api.clever.com/v2.1/',
        'client_id': '5d8a7b5eff6cbe25bc6e',
        'client_secret': 'ec6d2c060987e32cbe785f7f1a58a307a04cf0a4',
        'key_identifier': 'id',
        'page_size': 1000,
        'max_user_count': 0,
        'match_groups_by': 'name',
        'access_token': 'TEST_TOKEN'
    }

    return CleverConnector(options)


@mock.patch('oneroster.clever.requests.get')
def test_get_users(requests_get, mock_many_students, mock_teacher, clever_api):
    empty_repsonse = get_mock_api_response([])
    mock_student_response = [get_mock_api_response(mock_many_students), empty_repsonse]
    mock_teacher_response = [get_mock_api_response(mock_teacher), empty_repsonse]

    requests_get.side_effect = mock_student_response
    response = clever_api.get_users(user_filter='students')
    assert reduce(mock_many_students) == reduce(response)

    requests_get.side_effect = mock_teacher_response
    response = clever_api.get_users(user_filter='teachers')
    assert reduce(mock_teacher) == reduce(response)

    mock_many_students.extend(mock_teacher)
    mock_student_response.extend(mock_teacher_response)
    requests_get.side_effect = mock_student_response
    response = clever_api.get_users(user_filter='users')
    assert reduce(mock_many_students) == reduce(response)


@mock.patch('oneroster.clever.requests.get')
@mock.patch('oneroster.clever.CleverConnector.get_primary_key')
def test_get_users_for_section(get_key, requests_get, clever_api, mock_many_students, mock_teacher):
    # Empty response needed to end the make cap
    empty_repsonse = get_mock_api_response([])
    mock_student_response = [get_mock_api_response(mock_many_students), empty_repsonse]
    mock_teacher_response = [get_mock_api_response(mock_teacher), empty_repsonse]

    # Section key - not actually relevent here
    get_key.return_value = ['58da8c6b894273be680001fc']

    # Get students
    requests_get.side_effect = mock_student_response
    response = clever_api.get_users(user_filter='students',
                                    group_filter='sections',
                                    group_name='Class 003, Homeroom - Stark - 0')
    assert reduce(mock_many_students) == reduce(response)

    # Get students
    requests_get.side_effect = mock_teacher_response
    response = clever_api.get_users(user_filter='teachers',
                                    group_filter='sections',
                                    group_name='Class 003, Homeroom - Stark - 0')
    assert reduce(mock_teacher) == reduce(response)

    mock_many_students.extend(mock_teacher)
    mock_student_response.extend(mock_teacher_response)
    requests_get.side_effect = mock_student_response
    response = clever_api.get_users(user_filter='users',
                                    group_filter='sections',
                                    group_name='Class 003, Homeroom - Stark - 0')
    assert reduce(mock_many_students) == reduce(response)


@mock.patch('oneroster.clever.requests.get')
def test_make_call(requests_get, clever_api, mock_user_data):
    page_1 = get_mock_api_response(mock_user_data[0:2])
    page_2 = get_mock_api_response(mock_user_data[2:4])
    page_3 = get_mock_api_response([])

    requests_get.side_effect = [page_1, page_2, page_3]
    urls = clever_api.translate(None, 'students')[0]

    response = clever_api.make_call(url=urls)
    assert reduce(mock_user_data) == reduce(response)


@mock.patch('oneroster.clever.CleverConnector.make_call')
def test_get_primary_key(mock_make_call, clever_api, log_stream, mock_section_data):
    stream, logger = log_stream
    clever_api.logger = logger
    mock_make_call.return_value = mock_section_data

    keys = clever_api.get_primary_key("sections", "Class 202, Homeroom - Jones - 0")
    assert keys == ['58da8c6b894273be6800020a', '58da8c6b894273be5100020a']

    keys = clever_api.get_primary_key("sections", "Fake class")
    assert not keys

    stream.flush()
    logs = stream.getvalue()
    assert re.search('(No objects found for sections:).*(Fake class)', logs)

    stream.buf = ''
    clever_api.match_groups_by = 'bad'
    clever_api.get_primary_key("sections", "fake")
    stream.flush()
    logs = stream.getvalue()
    assert re.search("(No property: 'bad' was found on section for entity 'fake')", logs)

    # Get ID based on SIS ID
    clever_api.match_groups_by = "sis_id"
    keys = clever_api.get_primary_key("sections", "161-875-2356")
    assert keys == ['58da8c6b894273be68000236']

    # Get ID based on course
    clever_api.match_groups_by = 'course'
    keys = clever_api.get_primary_key("sections", "Math 101")
    assert keys == ['58da8c6b894273be680001fc']


@mock.patch('oneroster.clever.CleverConnector.make_call')
@mock.patch('oneroster.clever.CleverConnector.get_primary_key')
def test_get_sections_for_course(get_key, make_call, clever_api, mock_section_data):
    # Sections for ID 1
    data_1 = mock_section_data[0:2]

    # Sections for ID 2
    data_2 = mock_section_data[3:5]

    # These are the id's found for course name (totally arbitrary here)
    get_key.return_value = ['12345', '67892']

    # Each time we call, we get a response
    make_call.side_effect = [data_1, data_2]

    response = clever_api.get_sections_for_course('Math 101')
    data_1.extend(data_2)
    assert reduce(data_1) == collections.Counter(response)


@mock.patch('oneroster.clever.CleverConnector.make_call')
@mock.patch('oneroster.clever.CleverConnector.get_sections_for_course')
def test_get_users_for_course(get_sections, make_call, clever_api, mock_user_data):
    mock_students = mock_user_data[0:2]
    mock_teachers = mock_user_data[2:4]

    get_sections.return_value = ['12345']
    make_call.side_effect = [mock_students, mock_teachers]

    response = clever_api.get_users_for_course("Math 9", "users")
    assert reduce(mock_user_data) == reduce(response)


# def test_translate(clever_api):
#     calls = clever_api.translate('sections', 'users')
#     assert calls[0] == clever_api.clever_api.get_students_for_section_with_http_info
#     assert calls[1] == clever_api.clever_api.get_teachers_for_section_with_http_info
#     pytest.raises(ValueError, clever_api.translate, user_filter="x", group_filter="y")

def reduce(dictionary):
    return collections.Counter([x['id'] for x in dictionary])


def get_mock_api_response(data, status_code=200, headers=None):
    formatted = []
    [formatted.append({'data': u, 'uri': ''}) for u in data]

    body = {'data': formatted, 'links': []}
    response = Response()
    response._content = json.dumps(body).encode()
    response.status_code = status_code
    response.headers = headers

    return response


def get_mock_api_response_dataonly(data):
    return get_mock_api_response(data)[0].data


# Not a real test - just for producing data
# def test_data_generator(clever_api):
# res = clever_api.get_users(group_filter='sections',
#                                   user_filter='users',
#                                   group_name='Class 003, Homeroom - Stark - 0')

# clever_api.get_users(user_filter='teachers')
# clever_api.get_primary_key('sections', 'Class 003, Homeroom - Stark - 0')
# clever_api.get_sections_for_course('Class 001, Homeroom')


@pytest.fixture()
def mock_section_data():
    return [
        {
            'id': '58da8c6b894273be680001fc',
            'name': 'Class 003, Homeroom - Stark - 0',
            'sis_id': '278-002-1020',
            'course': 'Math 101'
        },
        {
            'id': '58da8c6b894273be6800020a',
            'name': 'Class 202, Homeroom - Jones - 0',
            'sis_id': '341-356-1315',
            'course': 'Art 101'
        },
        {
            'id': '58da8c6b894273be5100020a',
            'name': 'Class 202, Homeroom - Jones - 0',
            'sis_id': '754-1523-6311',
            'course': 'Sci 101'
        },
        {
            'id': '58da8c6b894273be68000236',
            'name': 'Grade 2 Math, Class 201 - Hammes - 3',
            'sis_id': '161-875-2356',
            'course': 'Geo 101'
        },
        {
            'id': '58da8c6b894273be68000222',
            'name': 'Kindergarten Math, Class 002 - Schoen - 1',
            'sis_id': '958-163-2145',
            'course': 'Alg 101'},
        {
            'id': '58da8c6b894273be68000242',
            'name': 'Mathematics, Class 601 - Goldner - 3',
            'sis_id': '762-561-6723',
            'course': 'Shop 101'}
    ]


@pytest.fixture()
def mock_user_data():
    return [
        {
            'id': '58da8c6b894224000242',
            'email': 'z.steve@example.net',
            'name': {'first': 'Steve', 'last': 'Ziemann', 'middle': 'G'},
            'school': '58da8c58155b940248000007',
            'sis_id': '100095233'
        },
        {
            'id': '58da8c6b89486y677765',
            'email': 'julia.r@example.org',
            'name': {'first': 'Julia', 'last': 'Runolfsdottir', 'middle': 'B'},
            'school': '58da8c58155b940248000007',
            'sis_id': '108028995'
        },
        {
            'id': '58da8c6b89427512faef3f',
            'email': 'sisko.b@example.net',
            'name': {'first': 'Benjamin', 'last': 'Sisko', 'middle': 'J'},
            'school': '58da8c58155b940248000007',
            'sis_id': '1001234233'
        },
        {
            'id': '58da8c75ghgdsdf0242',
            'email': 'picard.j@example.org',
            'name': {'first': 'Jean Luc', 'last': 'Picard', 'middle': ''},
            'school': '58da8c58155b940248000007',
            'sis_id': '108062341'
        }
    ]


@pytest.fixture()
def mock_many_students():
    return [{'id': '58da8c63d7dc0ca06800043e', 'name': {'first': 'Karen', 'last': 'Harvey', 'middle': 'D'}, 'email': 'karen.h@example.net', 'sis_id': '173157322'},
            {'id': '58da8c63d7dc0ca068000443', 'name': {'first': 'Adrianna', 'last': 'Sawayn', 'middle': 'A'}, 'email': 'adrianna.s@example.org', 'sis_id': '176057934'},
            {'id': '58da8c63d7dc0ca06800045f', 'name': {'first': 'Jonathan', 'last': 'Dietrich', 'middle': 'G'}, 'email': 'd.jonathan@example.com', 'sis_id': '206776810'},
            {'id': '58da8c63d7dc0ca06800047a', 'name': {'first': 'George', 'last': "O'Connell", 'middle': 'S'}, 'email': 'o_george@example.org', 'sis_id': '235286679'},
            {'id': '58da8c63d7dc0ca068000497', 'name': {'first': 'Kevin', 'last': 'Herman', 'middle': 'B'}, 'email': 'h_kevin@example.net', 'sis_id': '265863904'},
            {'id': '58da8c63d7dc0ca0680004ca', 'name': {'first': 'Alice', 'last': 'Fadel', 'middle': 'J'}, 'email': 'f_alice@example.org', 'sis_id': '297056232'},
            {'id': '58da8c64d7dc0ca068000562', 'name': {'first': 'Mark', 'last': 'McGlynn', 'middle': 'A'}, 'email': 'm.mark@example.net', 'sis_id': '427573397'},
            {'id': '58da8c64d7dc0ca0680005aa', 'name': {'first': 'Mark', 'last': 'Hackett', 'middle': 'E'}, 'email': 'h.mark@example.org', 'sis_id': '495684672'},
            {'id': '58da8c64d7dc0ca0680005c0', 'name': {'first': 'Linda', 'last': 'Abernathy', 'middle': 'C'}, 'email': 'linda.a@example.com', 'sis_id': '508410312'},
            {'id': '58da8c64d7dc0ca0680005c3', 'name': {'first': 'Julianne', 'last': 'Dicki', 'middle': 'C'}, 'email': 'd.julianne@example.net', 'sis_id': '510492620'},
            {'id': '58da8c64d7dc0ca0680005e7', 'name': {'first': 'Tammy', 'last': 'Robel', 'middle': 'R'}, 'email': 'tammy_r@example.net', 'sis_id': '547417208'},
            {'id': '58da8c64d7dc0ca068000640', 'name': {'first': 'Marcia', 'last': 'Rippin', 'middle': 'R'}, 'email': 'r_marcia@example.org', 'sis_id': '635560230'},
            {'id': '58da8c64d7dc0ca06800064b', 'name': {'first': 'Margaret', 'last': 'Grant', 'middle': 'D'}, 'email': 'margaret_g@example.net', 'sis_id': '641257513'},
            {'id': '58da8c64d7dc0ca068000674', 'name': {'first': 'Florence', 'last': 'Rowe', 'middle': 'P'}, 'email': 'florence_r@example.org', 'sis_id': '674331356'},
            {'id': '58da8c65d7dc0ca068000698', 'name': {'first': 'Mary', 'last': 'Rosenbaum', 'middle': 'P'}, 'email': 'r.mary@example.com', 'sis_id': '710689080'},
            {'id': '58da8c65d7dc0ca0680006f4', 'name': {'first': 'Kimberly', 'last': 'Mraz', 'middle': 'R'}, 'email': 'm.kimberly@example.org', 'sis_id': '800017226'},
            {'id': '58da8c65d7dc0ca068000715', 'name': {'first': 'Diana', 'last': 'Monahan', 'middle': 'E'}, 'email': 'm.diana@example.net', 'sis_id': '830604811'},
            {'id': '58da8c65d7dc0ca06800077d', 'name': {'first': 'Vivian', 'last': 'Kris', 'middle': 'K'}, 'email': 'vivian_k@example.net', 'sis_id': '926639679'},
            {'id': '58da8c65d7dc0ca0680007ab', 'name': {'first': 'Vanessa', 'last': 'Farrell', 'middle': 'C'}, 'email': 'vanessa_f@example.org', 'sis_id': '963452890'},
            {'id': '58da8c65d7dc0ca0680007b0', 'name': {'first': 'Jeffrey', 'last': 'Hettinger', 'middle': 'A'}, 'email': 'h.jeffrey@example.org', 'sis_id': '967155729'}]


@pytest.fixture()
def mock_teacher():
    return [{'id': '58da8c5da7a7e5a64700009c', 'name': {'first': 'Jessica', 'last': 'Stark', 'middle': 'R'}, 'email': 'stark_jessica@example.net', 'sis_id': '70'}]
