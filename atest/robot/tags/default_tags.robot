*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    tags/default_tags.robot
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Case ***
No Own Tags With Default Tags
    Check Test Tags    No Own Tags With Default Tags    03    four

Own Tags With Default Tags
    Check Test Tags    Own Tags With Default Tags    00    01    FOUR    viisi

Own Tags Empty With Default Tags
    Check Test Tags    Own Tags Empty With Default Tags
