*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/operating_system/path.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***
Join Path
    Check testcase  ${TESTNAME}

Join Paths
    Check testcase  ${TESTNAME}

Normalize Path
    Check testcase  ${TESTNAME}

Split Path
    Check testcase  ${TESTNAME}

Split Extension
    Check testcase  ${TESTNAME}

Forward Slash Works as Separator On All OSes
    Check testcase  ${TESTNAME}

Non-ASCII
    Check testcase  ${TESTNAME}

With Space
    Check testcase  ${TESTNAME}

