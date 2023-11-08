*** Settings ***
Test Tags       -in-settings    tag1    tag2    tag3    ${TAG}
Keyword Tags    -in-settings    kw1    kw2
Resource        -tag_syntax.resource

*** Variables ***
${TAG}          tag
${VAR}          -variable

*** Test Cases ***
Remove from test
    [Tags]    -tag2    tag4    -${tag}    --in-settings
    Remove from keyword

Remove from test using pattern
    [Tags]    -tag[12]
    Remove from keyword using pattern

Escaped
    [Tags]    \-escaped
    No Operation

Variable
    [Tags]    ${VAR}
    No Operation

*** Keywords ***
Remove from keyword
    [Tags]    -kw1
    No Operation
