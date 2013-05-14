*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/operating_system/path_expansion.txt
Force Tags      regression
Resource        atest_resource.txt

*** Test Cases ***
Tilde in path
    [Tags]  pybot  jybot
    Check testcase  ${TESTNAME}

Tilde and username in path
    [Tags]  pybot
    Run on python 2.5     Remove tags   regression
    Check testcase  ${TESTNAME}
