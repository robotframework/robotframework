*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/file_and_dir_existence.robot
Resource          atest_resource.robot

*** Test Cases ***
Should Exist
    Check Test Case    ${TESTNAME}

Should Exist With Non Default Message
    Check Test Case    ${TESTNAME}

Should Exist With Pattern
    Check Test Case    ${TESTNAME}

Glob In Name
    Check Test Case    ${TESTNAME}

Glob In Name Should Not Exist
    Check Test Case    ${TESTNAME}

Glob In Name File Should Not Exist
    Check Test Case    ${TESTNAME}

Glob In Name Directory Should Not Exist
    Check Test Case    ${TESTNAME}

Should Not Exist
    Check Test Case    ${TESTNAME}

Should Not Exist With Non Default Message
    Check Test Case    ${TESTNAME}

Should Not Exist With Pattern
    Check Test Case    ${TESTNAME}

File Should Exist
    Check Test Case    ${TESTNAME}

File Should Exist When Dir Exists
    Check Test Case    ${TESTNAME}

File Should Exist With Non Default Message
    Check Test Case    ${TESTNAME}

File Should Exist With Pattern
    Check Test Case    ${TESTNAME}

File Should Not Exist
    Check Test Case    ${TESTNAME}

File Should Not Exist With Non Default Message
    Check Test Case    ${TESTNAME}

File Should Not Exist With Pattern Matching One File
    Check Test Case    ${TESTNAME}

File Should Not Exist With Pattern Matching Multiple Files
    Check Test Case    ${TESTNAME}

Directory Should Exist
    Check Test Case    ${TESTNAME}

Directory Should Exist When File Exists
    Check Test Case    ${TESTNAME}

Directory Should Exist Exists With Non Default Message
    Check Test Case    ${TESTNAME}

Directory Should Exist With Pattern
    Check Test Case    ${TESTNAME}

Directory Should Not Exist
    Check Test Case    ${TESTNAME}

Directory Should Not Exist With Non Default Message
    Check Test Case    ${TESTNAME}

Directory Should Not Exist With Pattern Matching One Dir
    Check Test Case    ${TESTNAME}

Directory Should Not Exist With Pattern Matching Multiple Dirs
    Check Test Case    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
