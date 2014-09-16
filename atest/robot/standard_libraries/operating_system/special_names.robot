*** Settings ***
Documentation    Tests for different file and directory names.
...    These are, for most parts, tested also elsewhere.
...    Tests with non-ASCII chars having ordinal over 255 fail on Jython due to
...    http://bugs.jython.org/issue1658
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/operating_system/special_names.robot
Test Setup       Make Tests Failing On Jython/Windows Non Critical If Using That Combo
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
ASCII only file name
    Check Test Case    ${TESTNAME}

File name with spaces
    Check Test Case    ${TESTNAME}

Non-ASCII file name with ordinals < 255
    Check Test Case    ${TESTNAME}

Non-ASCII file name with ordinals > 255
    [Tags]    x-fails-on-windows-jython
    Check Test Case    ${TESTNAME}

ASCII only directory name
    Check Test Case    ${TESTNAME}

Directory name with spaces
    Check Test Case    ${TESTNAME}

Non-ASCII directory name with ordinals < 255
    Check Test Case    ${TESTNAME}

Non-ASCII directory name with ordinals > 255
    [Tags]    x-fails-on-windows-jython
    Check Test Case    ${TESTNAME}

*** Keywords ***
Make Tests Failing On Jython/Windows Non Critical If Using That Combo
    Run Keyword If    'x-fails-on-windows-jython' in @{TEST TAGS}
    ...    Run Keyword If    'jython' in '${INTERPRETER}' and '${:}' == ';'
    ...    Remove Tags    regression
