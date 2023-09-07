*** Settings ***
Resource          common_resource.robot

*** Variables ***
${RESOURCE_INDEX}    1

*** Test Cases ***
Test 1
    UK From Resource 1    ${GREETINGS}
