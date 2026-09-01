from robot.api.deco import keyword


def defined_twice():
    1 / 0  # noqa


@keyword("Defined twice")
def this_time_using_custom_name():
    2 / 0  # noqa


def defined_thrice():
    1 / 0  # noqa


def definedThrice():
    2 / 0  # noqa


def Defined_Thrice():
    3 / 0  # noqa


@keyword("Embedded ${arguments} twice")
def embedded1(arg):
    1 / 0  # noqa


@keyword("Embedded ${arguments match} TWICE")
def embedded2(arg):
    2 / 0  # noqa
