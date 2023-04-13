from robot.conf import Language


class Custom(Language):
    settings_header = 'H S'
    variables_header = 'H v'
    test_cases_header = 'h te'
    tasks_header = 'H Ta'
    keywords_header = 'H k'
    comments_header = 'h C'
    library_setting = 'L'
    resource_setting = 'R'
    variables_setting = 'V'
    name_setting = 'N'
    documentation_setting = 'D'
    metadata_setting = 'M'
    suite_setup_setting = 'S S'
    suite_teardown_setting = 'S T'
    test_setup_setting = 't s'
    task_setup_setting = 'ta s'
    test_teardown_setting = 'T tea'
    task_teardown_setting = 'TA tea'
    test_template_setting = 'T TEM'
    task_template_setting = 'TA TEM'
    test_timeout_setting = 't ti'
    task_timeout_setting = 'ta ti'
    test_tags_setting = 'T Ta'
    task_tags_setting = 'Ta Ta'
    keyword_tags_setting = 'K T'
    setup_setting = 'S'
    teardown_setting = 'TeA'
    template_setting = 'Tem'
    tags_setting = 'Ta'
    timeout_setting = 'ti'
    arguments_setting = 'A'
    given_prefix = set()
    when_prefix = set()
    then_prefix = set()
    and_prefix = set()
    but_prefix = set()
