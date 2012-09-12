*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/operating_system/remove_file.txt
Force Tags      regression  pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***

Remove File
    Check Test Case  ${TESTNAME}

Remove Files
    Check Test Case  ${TESTNAME}

Remove Non-ASCII File
    Check Test Case  ${TESTNAME}

Remove File With Space
    Check Test Case  ${TESTNAME}

Remove Files Using Glob Pattern
    Check Test Case  ${TESTNAME}

Remove Non-ASCII Files Using Glob Pattern
    # On OSX python glob does not handle NFD characters.
    [Tags]  x-exclude-on-osx-python
    Check Test Case  ${TESTNAME}

Remove Non-Existing File
    Check Test Case  ${TESTNAME}

Removing Directory As A File Fails
    Check Test Case  ${TESTNAME}

