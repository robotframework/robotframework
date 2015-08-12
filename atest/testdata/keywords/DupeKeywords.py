from robot.api.deco import keyword


def defined_twice():
    1/0

@keyword('Defined twice')
def this_time_using_custom_name():
    2/0

def defined_thrice():
    1/0

def definedThrice():
    2/0

def Defined_Thrice():
    3/0

@keyword('Embedded ${arguments} twice')
def embedded1(arg):
    1/0

@keyword('Embedded ${arguments match} TWICE')
def embedded2(arg):
    2/0
