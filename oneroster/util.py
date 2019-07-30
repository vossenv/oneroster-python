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
            filtered[k] = "<filtered>" if k in filtered_fields else v

    return filtered



