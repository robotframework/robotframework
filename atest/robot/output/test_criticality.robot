*** Settings ***
Resource  atest_resource.robot
Suite Setup  Run some tests and parse XML

*** Test Cases ***
Test Criticality Should Be Serialized Inside Status Tag
    Check Test Criticality in Output  0  yes
    Check Test Criticality in Output  1  no

*** Keywords ***
Run some tests and parse XML
    Run Tests   --noncritical fail  misc${/}pass_and_fail.robot
    ${SUITE}=  Get Element  ${OUTFILE}  suite
    Set Suite Variable  ${SUITE}

Check Test Criticality in Output
    [Arguments]  ${testindex}  ${expected criticality}
    ${test}=  Set Variable  ${suite.findall('test')[${testindex}]}
    Should Be Equal  ${test.find('status').get('critical')}
    ...   ${expected criticality}


