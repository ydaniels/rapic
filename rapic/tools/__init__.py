import time


class dotdict(dict):
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


