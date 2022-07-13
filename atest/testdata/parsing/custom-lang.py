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
    test_setup = 'T S'
    test_teardown = 'T Tea'
    test_template = 'T Tem'
    test_timeout = 'T Ti'
    test_tags = 'T Ta'
    keyword_tags = 'K T'
    setup = 'S'
    teardown = 'Tea'
    template = 'Tem'
    tags = 'Ta'
    timeout = 'Ti'
    arguments = 'A'
    bdd_prefixes = set()
