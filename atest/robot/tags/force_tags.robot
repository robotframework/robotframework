*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    tags/force_tags.robot
Resource          atest_resource.robot

*** Test Cases ***
No Own Tags With Force Tags
    Check Test Tags    No Own Tags With Force Tags    01    02

Own Tags With Force Tags
    Check Test Tags    Own Tags With Force Tags    00    01    02    FOUR    viisi

Own Tags Empty With Force Tags
    Check Test Tags    Own Tags Empty With Force Tags    01    02
