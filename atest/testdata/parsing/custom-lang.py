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
    documentation = 'S 1'
    metadata = 'S 2'
    suite_setup = 'S 3'
    suite_teardown = 'S 4'
    test_setup = 'S 5'
    test_teardown = 'S 6'
    test_template = 'S 7'
    force_tags = 'S 8'
    default_tags = 'S 9'
    test_timeout = 'S 10'
    setup = 'S 11'
    teardown = 'S 12'
    template = 'S 13'
    tags = 'S 14'
    timeout = 'S 15'
    arguments = 'S 16'
    return_ = 'S 17'
    bdd_prefixes = {}
