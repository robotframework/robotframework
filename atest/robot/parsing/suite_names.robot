*** Settings ***
Documentation     Run testdata and validate that suite names are set correctly
Suite Setup     Run Tests    ${EMPTY}    misc/suites
Resource        atest_resource.robot
# Test Tags       suite_naming

*** Test Cases ***
Simple Custom Suite Name
    Should Be Equal As Strings    ${Suite.suites[2].name}    Subsuites
    Should Be Equal As Strings    ${Suite.suites[2].suites[0].name}    Custom sub1 Name

Simple Default File Suite Name
    Should Be Equal As Strings    ${Suite.suites[2].name}    Subsuites
    Should Be Equal As Strings    ${Suite.suites[2].suites[1].name}    Sub2

Cutom Suite Name With Parent init
    Should Be Equal As Strings    ${Suite.suites[3]}    Parent Suite Name
    Should Be Equal As Strings    ${Suite.suites[3].suites[0].name}    Sub.Suite.4
    Should Be Equal As Strings    ${Suite.suites[3].suites[2].name}    SubSuite333

Multi Root Custom Suite Name
    Should Be Equal As Strings    ${Suite.suites[3].suites[1].name}    SubParentSuite3Name
    Should Be Equal As Strings    ${Suite.suites[3].suites[1].suites[0].name}    Another Custom Sub Suite