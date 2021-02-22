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

Space After Newline Is parsed
    Check Test Case    ${TEST NAME}

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
    Length should be      ${ERRORS}    0

Pipe
    Check Test Case    ${TEST NAME}
