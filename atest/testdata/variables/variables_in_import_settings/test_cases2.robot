*** Settings ***
Resource          common_resource.robot

*** Variables ***
${RESOURCE_INDEX}    2

*** Test Cases ***
Test 2
    UK From Resource 2    ${GREETINGS}
