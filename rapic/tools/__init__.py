import json

def flatten_hook(obj):
    for key, value in obj.items():
        if isinstance(value, str):
            try:
                obj[key] = json.loads(value, object_hook=flatten_hook)
            except ValueError:
                pass
    return obj


def json_loads_nested(data):
    return json.loads(data, object_hook=flatten_hook)


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def delete_keys(data):
    """
    set  data values  to None
    :param data:
    :return:
    """
    return {key: None for key in data}


def dict_merge(base_dct, merge_dct, add_keys=True):
    """
    Recursively merge dict from
    https://gist.github.com/CMeza99/5eae3af0776bef32f945f34428669437
    """
    rtn_dct = base_dct.copy()
    if add_keys is False:
        merge_dct = {key: merge_dct[key] for key in set(rtn_dct).intersection(set(merge_dct))}

    rtn_dct.update({
        key: dict_merge(rtn_dct[key], merge_dct[key], add_keys=add_keys)
        if isinstance(rtn_dct.get(key), dict) and isinstance(merge_dct[key], dict)
        else merge_dct[key]
        for key in merge_dct.keys()
    })
    return rtn_dct
