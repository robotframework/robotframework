*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    tags/force_tags.robot
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Case ***
No Own Tags With Force Tags
    Check Test Tags    No Own Tags With Force Tags    01    02

Own Tags With Force Tags
    Check Test Tags    Own Tags With Force Tags    00    01    02    FOUR    viisi

Own Tags Empty With Force Tags
    Check Test Tags    Own Tags Empty With Force Tags    01    02
