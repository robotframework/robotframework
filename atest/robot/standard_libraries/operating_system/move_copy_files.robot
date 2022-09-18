*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/move_copy_files.robot
Resource          atest_resource.robot

*** Test Cases ***
Move One File With Move Files
    Check Test Case    ${TESTNAME}

Move Files fails when no destination
    Check Test Case    ${TESTNAME}

Move Files without arguments fails
    Check Test Case    ${TESTNAME}

Move Multiple Files
    Check Test Case    ${TESTNAME}

Move Multiple Files From Multiple Directories
    Check Test Case    ${TESTNAME}

Move List of Files
    Check Test Case    ${TESTNAME}

Move List of Files with Patterns
    Check Test Case    ${TESTNAME}

Moving Non-existing Files
    Check Test Case    ${TESTNAME}

Copy One File To Dir With Copy Files
    Check Test Case    ${TESTNAME}

Copy Files fails when no destination
    Check Test Case    ${TESTNAME}

Copy Files without arguments fails
    Check Test Case    ${TESTNAME}

Copy Files destination can not be an existing file
    Check Test Case    ${TESTNAME}

Move Files destination can not be an existing file
    Check Test Case    ${TESTNAME}

Copy Files directory will be created if it does not exist
    Check Test Case    ${TESTNAME}

Move Files directory will be created if it does not exist
    Check Test Case    ${TESTNAME}

Copy One File To File With Copy Files
    Check Test Case    ${TESTNAME}

Copy Multiple Files
    Check Test Case    ${TESTNAME}

Copy Multiple Files From Multiple Directories
    Check Test Case    ${TESTNAME}

Copy List of Files
    Check Test Case    ${TESTNAME}

Copy List of Files with Patterns
    Check Test Case    ${TESTNAME}

Copying Non-existing Files
    Check Test Case    ${TESTNAME}

Copying And Moving With backslash in glob pattern
    Check Test Case    ${TESTNAME}

Copying From Name With Glob
    Check Test Case    ${TESTNAME}

Moving From Name With Glob
    Check Test Case    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}
