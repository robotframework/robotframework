try:
    from UserDict import UserDict
except ImportError:
    from collections import UserDict


def get_user_dict(**kwargs):
    return UserDict(**kwargs)
