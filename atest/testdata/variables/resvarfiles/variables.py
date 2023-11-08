class _Object:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return repr(self.name)


STRING = 'Hello world!'
INTEGER = 42
FLOAT = -1.2
BOOLEAN = True
NONE_VALUE = None
ESCAPES = 'one \\ two \\\\ ${non_existing}'
NO_VALUE = ''
LIST = ['Hello', 'world', '!']
LIST_WITH_NON_STRINGS = [42, -1.2, True, None]
LIST_WITH_ESCAPES = ['one \\', 'two \\\\', 'three \\\\\\', '${non_existing}']
OBJECT = _Object('dude')

LIST__ONE_ITEM = ['Hello again?']
LIST__LIST_2 = ['Hello', 'again', '?']
LIST__LIST_WITH_ESCAPES_2 = LIST_WITH_ESCAPES[:]
LIST__EMPTY_LIST = []
LIST__OBJECTS = [STRING, INTEGER, LIST, OBJECT]

lowercase = 'Variable name in lower case'
LIST__lowercase_list = [lowercase]
Und_er__scores_____ = 'Variable name with under scores'
LIST________UN__der__SCO__r_e_s__liST__ = [Und_er__scores_____]


PRIORITIES_1 = PRIORITIES_2 = PRIORITIES_3 = PRIORITIES_4 = PRIORITIES_4B \
               = 'Variable File'
