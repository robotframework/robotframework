*** Settings ***
Test Template      Should Be Equal
Resource           catenate_scalars_in_variable_table.resource

*** Test Cases ***
Catenated in resource 2
    ${CATENATED IN RESOURCE 1}    aaabbbcccddd
    ${CATENATED IN RESOURCE 2}    1sep2
