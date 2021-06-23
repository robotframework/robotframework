*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/should_be.robot
Resource          atest_resource.robot

*** Test Cases ***
Should Be String Positive
    Check Test Case    ${TESTNAME}

Should Be String Negative
    Check Test Case    ${TESTNAME}

Bytes are strings in Python 2
    [Tags]    require-py2    no-ipy
    Check Test Case    ${TESTNAME}

Bytes are not strings in Python 3
    [Tags]    require-py3
    Check Test Case    Bytes are not strings in Python 3 and IronPython

Bytes are not strings in IronPython
    [Documentation]
    ...    `isinstance(b'', basestring) is True` on IronPython 2.7.7 but it wasn't on earlier 2.7 versions.
    ...    For us it is easier to handle IronPython same way regardless the minor version.
    [Tags]    require-ipy
    Check Test Case    Bytes are not strings in Python 3 and IronPython

Should Not Be String Positive
    Check Test Case    ${TESTNAME}

Should Not Be String Negative
    Check Test Case    ${TESTNAME}

Should Be Unicode String Positive
    Check Test Case    ${TESTNAME}

Should Be Unicode String Negative
    [Tags]    no-ipy
    Check Test Case    ${TESTNAME}

Should Be Byte String Positive
    Check Test Case    ${TESTNAME}

Should Be Byte String Negative
    [Tags]    no-ipy
    Check Test Case    ${TESTNAME}

Should Be Lower Case Positive
    Check Test Case    ${TESTNAME}

Should Be Lower Case Negative
    Check Test Case    ${TESTNAME}

Should Be Upper Case Positive
    Check Test Case    ${TESTNAME}

Should Be Upper Case Negative
    Check Test Case    ${TESTNAME}

Should Be Title Case Positive
    Check Test Case    ${TESTNAME}

Should Be Title Case Negative
    Check Test Case    ${TESTNAME}

Should Be Title Case With Excludes
    Check Test Case    ${TESTNAME}

Should Be Title Case With Regex Excludes
    Check Test Case    ${TESTNAME}

Should Be Title Case Works With ASCII Bytes On Python 2
    [Tags]    require-py2    no-ipy
    Check Test Case    ${TESTNAME}

Should Be Title Case Does Not Work With ASCII Bytes On Python 2
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

Should Be Title Case Does Not Work With Non-ASCII Bytes
    Check Test Case    ${TESTNAME}
