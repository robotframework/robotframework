*** Settings ***
Suite Setup        Run Tests    ${EMPTY}    running/timeouts_with_logging.robot
Resource           atest_resource.robot

*** Test Cases ***
Timeouts with programmatic logging
    Should Contain Tests    ${SUITE}
    ...    RF logger 1    RF logger 2    RF logger 3    RF logger 4    RF logger 5
    ...    Python logging 1    Python logging 2    Python logging 3    Python logging 4    Python logging 5
