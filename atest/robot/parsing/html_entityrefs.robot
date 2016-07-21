*** Settings ***
Documentation   Tests for HTML entity and character references. Former are escapes like '&auml;' and latter are in format '&#82;'.
Suite Setup     Run Tests  ${EMPTY}  parsing/html_entityrefs.html
Resource        atest_resource.robot

*** Test Cases ***
Scandinavian Letters
    Check Test Case    ${TEST NAME}

XML Escapes
    Check Test Case    ${TEST NAME}

Other Escapes
    Check Test Case    ${TEST NAME}

Numerical Escapes
    [Documentation]  These are character references
    Check Test Case    ${TEST NAME}

Variables using escapes
    Check Test Case    ${TEST NAME}

