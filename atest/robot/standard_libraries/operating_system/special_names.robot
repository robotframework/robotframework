*** Settings ***
Documentation    Tests for different file and directory names.
...              These are, for most parts, tested also elsewhere.
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/operating_system/special_names.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
ASCII only file name
    Check Test Case    ${TESTNAME}

File name with spaces
    Check Test Case    ${TESTNAME}

Non-ASCII file name with ordinals < 255
    [Documentation]    Fails on OSX because python's glob pattern handling bug
    Make test non-critical if    sys.platform=='darwin'
    Check Test Case    ${TESTNAME}

Non-ASCII file name with ordinals > 255
    [Documentation]    Fails on OSX because python's glob pattern handling bug
    Make test non-critical if    sys.platform=='darwin'
    Check Test Case    ${TESTNAME}

ASCII only directory name
    Check Test Case    ${TESTNAME}

Directory name with spaces
    Check Test Case    ${TESTNAME}

Non-ASCII directory name with ordinals < 255
    Check Test Case    ${TESTNAME}

Non-ASCII directory name with ordinals > 255
    Check Test Case    ${TESTNAME}

