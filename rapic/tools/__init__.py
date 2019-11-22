import time


def delete_keys(data):
    """
    set  data values  to None
    :param data:
    :return:
    """
    return {key: None for key in data}


def get_time_stamp():
    return str(int(time.time()))


def get_time_stamp_ms():
    return str(int(time.time() * 1000))