from robot.conf import Language


class Custom(Language):
    setting_headers = {'H 1'}
    variable_headers = {'H 2'}
    test_case_headers = {'H 3'}
    task_headers = {'H 4'}
    keyword_headers = {'H 5'}
    comment_headers = {'H 6'}
    library = 'L'
    resource = 'R'
    variables = 'V'
    documentation = 'D'
    metadata = 'M'
    suite_setup = 'S S'
    suite_teardown = 'S T'
    test_setup = 't s'
    test_teardown = 'T tea'
    test_template = 'T TEM'
    test_timeout = 't ti'
    test_tags = 'T Ta'
    keyword_tags = 'K T'
    setup = 'S'
    teardown = 'TeA'
    template = 'Tem'
    tags = 'Ta'
    timeout = 'ti'
    arguments = 'A'
    bdd_prefixes = set()
