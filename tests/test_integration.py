import pytest

from oneroster.clever import *


@pytest.fixture()
def clever_api():
    options = {
        'host': 'https://api.clever.com/v2.1/',
        'client_id': '',
        'client_secret': '',
        'key_identifier': 'id',
        'page_size': 1000,
        'max_user_count': 2,
        'match_groups_by': 'name',
        'access_token': 'TEST_TOKEN'
    }

    return CleverConnector(options)


@pytest.fixture(scope='module')
def vcr(vcr):
    vcr.serializer = 'yaml'
    vcr.record_mode = 'once'
    vcr.cassette_library_dir = 'fixtures/cassettes'
    return vcr


@pytest.mark.vcr()
def test_simple(clever_api):
    x = clever_api.get_users(user_filter='teachers')

    print()
