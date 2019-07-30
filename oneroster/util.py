


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