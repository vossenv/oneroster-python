
from oneroster.util import *
import pytest

def test_match():

    mock_object = {
            'id': '58da8c6b894273be680001fc',
            'name': 'Class 003, Homeroom - Stark - 0',
            'sis_id': '278-002-1020',
            'course': 'Math 101'
    }


    match_on = 'name'
    assert match_object(mock_object, match_on, mock_object['name'])

    match_on = ['naMe', 'cOurse']
    assert match_object(mock_object, match_on, mock_object['name'])
    assert match_object(mock_object, match_on, 'MATH 101')

    match_on = ('name', 'course')
    assert match_object(mock_object, match_on, mock_object['name'])
    assert match_object(mock_object, match_on, mock_object['course'])

    match_on = {'name','course'}
    assert match_object(mock_object, match_on, mock_object['name'])
    assert match_object(mock_object, match_on, mock_object['course'])

    pytest.raises(TypeError, match_object, [mock_object, match_on, {}])
    pytest.raises(TypeError, ['a','b'], [mock_object, match_on, []])


