*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    tags/no_force_no_default_tags.robot
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Case ***
No Own Tags No Force Nor Default
    Check Test Tags    No Own Tags No Force Nor Default

Own Tags No Force Nor Default
    Check Test Tags    Own Tags No Force Nor Default    00    01    FOUR    viisi

Own Tags Empty No Force Nor Default
    Check Test Tags    Own Tags Empty No Force Nor Default
