*** Settings ***
Force Tags      -literal-with-force
Default Tags    -literal-with-default
Resource        -tag_syntax.resource

*** Variables ***
${TAG}          -literal-with-variable

*** Test Cases ***
Deprecation warning
    [Tags]    -warn-with-test
    Keyword
    Keyword In Resource

Escaped
    [Tags]    \-literal-escaped
    No Operation

Variable
    [Tags]    ${TAG}
    No Operation

*** Keywords ***
Keyword
    [Tags]    -warn-with-keyword
    No Operation
