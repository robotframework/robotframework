from robot.utils import OrderedDict


def get_variables(*args):
    if args:
        return dict((args[i], args[i+1]) for i in range(0, len(args), 2))
    return {'LIST__list': ['1', '2', 3],
            'LIST__tuple': ('1', '2', 3),
            'LIST__generator': xrange(5),
            'DICT__dict': {'a': 1, 2: 'b'},
            'DICT__ordered': OrderedDict((chr(o), o) for o in range(97, 107))}
