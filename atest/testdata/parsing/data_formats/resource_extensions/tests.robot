*** Settings ***
Resource         resource.resource
Resource         resource.robot
Resource         resource.txt
Resource         resource.TSV
Resource         resource.rst
Resource         resource.reST
Resource         resource.rsrc
Resource         resource.json
Resource         resource.invalid

*** Test Cases ***
Resource with '*.resource' extension
    Keyword in resource.resource
    Keyword in nested.resource
    Should Be Equal    ${RESOURCE}    resource.resource
    Should Be Equal    ${NESTED}      nested.resource
    Log    ${RESOURCE}
    Log    ${NESTED}

Resource with '*.robot' extension
    Keyword in resource.robot
    Should Be Equal    ${ROBOT}    resource.robot

Resource with '*.txt' extension
    Keyword in resource.txt
    Should Be Equal    ${TXT}    resource.txt

Resource with '*.tsv' extension
    Keyword in resource.tsv
    Should Be Equal    ${TSV}    resource.TSV

Resource with '*.rst' extension
    Keyword in resource.rst
    Should Be Equal    ${RST}    resource.rst

Resource with '*.rest' extension
    Keyword in resource.rest
    Should Be Equal    ${REST}    resource.reST

Resource with '*.rsrc' extension
    Keyword in resource.json
    Should Be Equal    ${JSON}    resource.json

Resource with '*.json' extension
    Keyword in resource.json
    Should Be Equal    ${JSON}    resource.json

Resource with invalid extension
    [Documentation]    FAIL    No keyword with name 'Keyword in resource.invalid' found.
    Keyword in resource.invalid
