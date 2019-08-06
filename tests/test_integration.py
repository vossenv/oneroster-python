import pytest
import yaml
import collections
from oneroster.clever import *


@pytest.fixture()
def clever_api():
    options = {
        'host': 'https://api.clever.com/v2.1/',
        'key_identifier': 'id',
        'page_size': 1000,
        'max_users': 0,
        'match_on': 'name',
        'access_token': 'TEST_TOKEN'
    }

    return CleverConnector(**options)


@pytest.fixture()
def source_data():
    with open('fixtures/comparison_data.yaml', 'r') as stream:
        yield yaml.safe_load(stream)


@pytest.fixture(scope='module')
def vcr(vcr):
    vcr.serializer = 'yaml'
    vcr.record_mode = 'new_episodes'
    vcr.cassette_library_dir = 'fixtures/cassettes'
    vcr.match_on = ['method', 'host', 'path', 'query']
    return vcr


@pytest.mark.vcr()
def test_simple(clever_api, source_data):
    clever_api.max_users = 100
    response = clever_api.get_users(user_filter='students')
    t = [r['id'] for r in response]
    x = collections.Counter(t) == collections.Counter(source_data['test_simple'])

    print()
