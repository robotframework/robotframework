class MyObject:

    def __init__(self, value):
        self.value = value

    def __int__(self):
        return 42 // self.value

    def __str__(self):
        return 'MyObject'


def get_variables():
    return {'object': MyObject(1),
            'object_failing': MyObject(0)}
