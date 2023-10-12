*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    tags/default_and_force_tags.robot
Resource          atest_resource.robot

*** Test Cases ***
No Own Tags
    Check Test Tags    No Own Tags    01    02    03    four

Own Tags
    Check Test Tags    Own Tags    00    01    02    FOUR    viisi

Own Tags Empty
    Check Test Tags    Own Tags Empty    01    02
