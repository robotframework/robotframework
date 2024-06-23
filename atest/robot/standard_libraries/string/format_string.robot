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

Template can contain '=' without escaping
    Check Test Case    ${TESTNAME}

Format String From Template File
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Reading Template Message    ${tc.kws[0].msgs[0]}    format_string_template.txt

Format String From Template Non-ASCII File
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Reading Template Message    ${tc.kws[0].msgs[0]}    format_string_nonasccii_template.txt

Format String From Trailling Whitespace Template File
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Reading Template Message    ${tc.kws[0].msgs[0]}    format_string_trailling_white_space_template.txt

Attribute access
    Check Test Case    ${TESTNAME}

Item access
    Check Test Case    ${TESTNAME}

Format Spec
    Check Test Case    ${TESTNAME}

*** Keywords ***
Check Reading Template Message
    [Arguments]    ${msg}    ${file}
    ${path} =    Normalize Path    ${DATADIR}/standard_libraries/string/${file}
    Check Log Message    ${msg}    Reading template from file <a href="${path}">${path}</a>.    html=True
