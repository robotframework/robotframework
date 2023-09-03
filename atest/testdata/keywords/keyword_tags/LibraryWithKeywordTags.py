from robot.api.deco import keyword


def library_keyword_tags_with_attribute():
    pass

library_keyword_tags_with_attribute.robot_tags = ['first', 'second']


@keyword(tags=('one', 2, '2', ''))
def library_keyword_tags_with_decorator():
    pass


def library_keyword_tags_with_documentation():
    """Summary line

    Tags: are read only from the last line

    Tags: one, two words"""
    pass


@keyword(tags=['one', 2])
def library_keyword_tags_with_documentation_and_attribute():
    """Tags: one, two words"""
    pass


@keyword(tags=42)
def invalid_library_keyword_tags():
    pass
