*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/keywords_implemented_in_c.robot
Resource          atest_resource.robot

*** Test Cases ***
Use with correct arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[-1].msgs[0]}    This is a bit weird ...

Use with incorrect arguments
    ${error} =    Set Variable If    ${INTERPRETER.is_pypy} or ${INTERPRETER.version_info} >= (3, 7)
    ...    Keyword 'KeywordsImplementedInC.Eq' expected 2 arguments, got 3.
    ...    STARTS: TypeError:
    Check Test Case    ${TEST NAME}    FAIL    ${error}

Built-ins not set to attributes are not exposes
    Check Test Case    ${TEST NAME}
