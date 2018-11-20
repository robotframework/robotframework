*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/format_string.robot
Resource          atest_resource.robot

*** Test Cases ***
Format String With Positional Argument
    Check Test Case    ${TESTNAME}

Format String With Positional Arguments
    Check Test Case    ${TESTNAME}

Format String With Named Search Replace Argument
    Check Test Case    ${TESTNAME}

Format String With Named Search Replace Arguments
    Check Test Case    ${TESTNAME}

Format String With Named And Search Replace Arguments
    Check Test Case    ${TESTNAME}

Format String From Non-ASCII Template
    Check Test Case    ${TESTNAME}

Format String From Template File
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Reading template from file <a href="/home/elyssonmr/projects/robotframework/atest/testdata/standard_libraries/string/format_string_template.txt">/home/elyssonmr/projects/robotframework/atest/testdata/standard_libraries/string/format_string_template.txt</a>    html=True

Format String From Template Non-ASCII File
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Reading template from file <a href="/home/elyssonmr/projects/robotframework/atest/testdata/standard_libraries/string/format_string_nonasccii_template.txt">/home/elyssonmr/projects/robotframework/atest/testdata/standard_libraries/string/format_string_nonasccii_template.txt</a>    html=True

Format String From Trailling Whitespace Template File
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Reading template from file <a href="/home/elyssonmr/projects/robotframework/atest/testdata/standard_libraries/string/format_string_trailling_white_space_template.txt">/home/elyssonmr/projects/robotframework/atest/testdata/standard_libraries/string/format_string_trailling_white_space_template.txt</a>    html=True

Attribute access
    Check Test Case    ${TESTNAME}

Item access
    Check Test Case    ${TESTNAME}
