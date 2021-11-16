*** Settings ***
Documentation    This suite should be split. Please don't add more tests but
...              create a new suite and move related tests from here to it too.
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/process_library.robot
Resource         atest_resource.robot

*** Test Cases ***
Library Namespace should be global
    Check Test Case    ${TESTNAME}

Error in exit code and stderr output
    Check Test Case    ${TESTNAME}

Start And Wait Process
    Check Test Case    ${TESTNAME}

Change Current Working Directory
    Check Test Case    ${TESTNAME}

Running a process in a shell
    Check Test Case    ${TESTNAME}

Input things to process
    Check Test Case    ${TESTNAME}

Assign process object to variable
    Check Test Case    ${TESTNAME}

Get process id
    Check Test Case    ${TESTNAME}
