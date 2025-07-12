# None of these decorators should be exposed as keywords.
from os.path import abspath

from robot.api.deco import keyword, not_keyword

not_keyword(abspath)


def exposed_in_module():
    pass


@not_keyword
def not_exposed_in_module():
    pass


@keyword
@not_keyword
def keyword_and_not_keyword():
    pass


def not_exposed_by_setting_attribute():
    pass


not_exposed_by_setting_attribute.robot_not_keyword = True
