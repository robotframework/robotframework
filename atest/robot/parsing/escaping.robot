*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    parsing/escaping.robot
Resource        atest_resource.robot

*** Test Cases ***
Spaces In Variable Table
    Check Test Case    ${TEST NAME}

Leading And Trailing Spaces In Variable Table
    Check Test Case    ${TEST NAME}

Backslash In Variable Table
    Check Test Case    ${TEST NAME}

Newline, Tab And Carriage Return In Variable Table
    Check Test Case    ${TEST NAME}

Escaping Variables In Variable Table
    Check Test Case    ${TEST NAME}

Escaping From List Variable In Variable Table
    Check Test Case    ${TEST NAME}

Non Strings Are Ok In Variable Table
    Check Test Case    ${TEST NAME}

Remove Spaces Before And After
    Check Test Case    ${TEST NAME}

Remove Extra Spaces Between
    Check Test Case    ${TEST NAME}

Escaping Space
    Check Test Case    ${TEST NAME}

Backslash
    Check Test Case    ${TEST NAME}

New Line
    Check Test Case    ${TEST NAME}

Ignoring Space After Newline Is Deprecated
    ${tc} =    Check Test Case    ${TEST NAME}
    ${message} =    Catenate
    ...    Ignoring space after '\\n' is deprecated.
    ...    For more info see: https://github.com/robotframework/robotframework/issues/3333
    Check log message    ${ERRORS}[0]    ${message}    WARN
    Check log message    ${ERRORS}[1]    ${message}    WARN
    Check log message    ${tc.kws[0].msgs[0]}    ${message}    WARN
    Check log message    ${tc.kws[0].msgs[1]}    ${message}    WARN

Carrriage Return
    Check Test Case    ${TEST NAME}

Tabulator
    Check Test Case    ${TEST NAME}

Valid \\x Escape
    Check Test Case    ${TEST NAME}

Invalid \\x Escape
    Check Test Case    ${TEST NAME}

Valid \\u Escape
    Check Test Case    ${TEST NAME}

Invalid \\u Escape
    Check Test Case    ${TEST NAME}

Valid \\U (32bit) Escape
    Check Test Case    ${TEST NAME}

Invalid \\U (32bit) Escape
    Check Test Case    ${TEST NAME}

\\U (32bit) Escape Above Valid Range
    Check Test Case    ${TEST NAME}

Hash
    Check Test Case    ${TEST NAME}

Any Character Escaped
    Check Test Case    ${TEST NAME}

Escaping Variables
    Check Test Case    ${TEST NAME}

Escaping Variables With User Keywords
    Check Test Case    ${TEST NAME}

No Errors Should Have Occurred
    Length should be      ${ERRORS}    2    # Warnings due to '\n ' deprecation.

Pipe
    Check Test Case    ${TEST NAME}
