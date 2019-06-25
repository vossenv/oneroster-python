import pytest
import tests.util as util


root_config_clever =  {
        'host': 'https://api.clever.com/v2.1/',
        'client_id': '5d8a7b5eff6cbe25bc6e',
        'client_secret': 'ec6d2c060987e32cbe785f7f1a58a307a04cf0a4',
        'key_identifier': 'id',
        'page_size': 1000,
        'max_user_count': 0,
        'match_groups_by': 'name',
        'access_token': 'TEST_TOKEN'
    }

root_config_classlink = {
        'host': 'https://api.clever.com/v2.1/',
        'client_id': '5d8a7b5eff6cbe25bc6e',
        'client_secret': 'ec6d2c060987e32cbe785f7f1a58a307a04cf0a4',
        'key_identifier': 'id',
        'page_size': 1000,
        'max_user_count': 0,
        'match_groups_by': 'name',
        'access_token': 'TEST_TOKEN'
    }

params = [root_config_clever, root_config_classlink]

@pytest.mark.parametrize("options", params)
def test_param_options(options):
    print(options)
    pass



