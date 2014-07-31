*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    tags/default_and_force_tags.txt
Force Tags        regression    jybot    pybot
Resource          atest_resource.txt

*** Test Case ***
No Own Tags
    Check Test Tags    No Own Tags    01    02    03    four

Own Tags
    Check Test Tags    Own Tags    00    01    02    FOUR    viisi

Own Tags Empty
    Check Test Tags    Own Tags Empty    01    02
