
import collections
import six

def decode_string(string):
    try:
        decoded = string.decode()
    except:
        decoded = str(string)
    return decoded.lower().strip()


def filter_dict(dict, filtered_fields=None):
    if not filtered_fields:
        return dict

    filtered = {}
    for k, v in dict.items():
        if isinstance(v,str):
            filtered[k] = "*******" if k in filtered_fields else v

    return filtered

def log_group_details(user_filter, group_filter, group_name, logger):
    group_desc = "" if not group_filter else group_filter + " / " + group_name + " / "
    logger.info("Executing requests for: " + group_desc + user_filter)

def log_followup_details(count, logger):
    logger.info(str(count) + " users returned")

def log_call_details(url, logger):
    logger.info("Getting users from: " + url)
    
def log_bad_json(e, object):
    return "Cannot parse json response: " + str(e) + ": " + str(object)

def log_bad_response(code, text):
    return "Call was not successful: " + str(code) + ": " + decode_string(text)

def log_failed_call(e):
    return "Call to clever failed. Reason: " + str(e)

def log_bad_key_id(id):
    return 'Key identifier: ' + id + ' not a valid identifier'

def log_bad_matcher_warning(group_filter, group_name, match_on):
    return ("No objects found for " + 
            group_filter + ": '" + 
            group_name + "' - possible bad matcher (" 
            + str(match_on) + ")?")

def match_object(object, match_on, value):
    if not isinstance(object, dict):
        raise TypeError("Invalid comparison: must be dictionary to compare: " + str(object))
    if isinstance(match_on, collections.MutableMapping):
        raise TypeError("Error! Dictionary not allowed for match keys: " + str(match_on))
    elif isinstance(match_on, str):
        match_on = [match_on]

    value = decode_string(value)
    decoded_obj = {decode_string(k): decode_string(v) for k, v in six.iteritems(object)}
    try:
        for field in iter(match_on):
            field = decode_string(field)
            if field in decoded_obj and decoded_obj[field] == value:
                return True
        return False
    except TypeError as e:
        raise TypeError("Error: specified match object is not string or iterable: "
                        + str(match_on) + " --- " + str(e))
