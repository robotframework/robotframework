*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/operating_system/file_and_dir_moving_and_copying.txt
Force Tags       regression    pybot    jybot
Resource         atest_resource.txt

*** Test Cases ***
Move File
    Check Test Case    ${TESTNAME}

Copy File
    Check Test Case    ${TESTNAME}

Copy File With Glob Pattern
    Check Test Case    ${TESTNAME}

Move File With Glob Pattern
    Check Test Case    ${TESTNAME}

Move File With Glob Pattern With Multiple Matches Fails
    Check Test Case    ${TESTNAME}

Copy File With Glob Pattern With Multiple Matches Fails
    Check Test Case    ${TESTNAME}

Copy File With Glob Pattern With No Matches Fails
    Check Test Case    ${TESTNAME}

Move File With Glob Pattern With No Matches Fails
    Check Test Case    ${TESTNAME}

Copy File when destination exists should be ok
    Check Test Case    ${TESTNAME}

Copy File when destination is a directory
    Check Test Case    ${TESTNAME}

Copy File when destination is a directory and file with same name exists
    Check Test Case    ${TESTNAME}

Move File To Existing Dir
    Check Test Case    ${TESTNAME}

Move File To Non-Existing Dir
    Check Test Case    ${TESTNAME}

Move File Using Just File Name
    Check Test Case    ${TESTNAME}

Moving Non-Existing File Fails
    Check Test Case    ${TESTNAME}

Move Directory
    Check Test Case    ${TESTNAME}

Move Directory To Existing Dir
    Check Test Case    ${TESTNAME}

Move Directory To Non-Existing Dir Tree
    Check Test Case    ${TESTNAME}

Move Directory Using Just Dir Name
    Check Test Case    ${TESTNAME}

Moving Non-Existing Directory Fails
    Check Test Case    ${TESTNAME}
