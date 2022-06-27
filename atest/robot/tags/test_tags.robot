*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    tags/force_tags.robot
Resource          atest_resource.robot

*** Test Cases ***
Test Tags
    Run Tests    ${EMPTY}    tags/test_tags.robot
    Check Test Tags    No own tags    tags    test
    Check Test Tags    Own tags       tags    test    own
    Should Be Empty    ${ERRORS}


Test Tags and Force Tags cannot be used together
    Run Tests    ${EMPTY}    tags/test_tags_and_force_tags_cannot_be_used_together.robot
    Check Test Tags    No own tags    tags    test
    Check Test Tags    Own tags       tags    test    own
    Error In File    0    tags/test_tags_and_force_tags_cannot_be_used_together.robot    3
    ...    Setting 'Force Tags' is allowed only once. Only the first value is used.

