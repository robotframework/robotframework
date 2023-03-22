*** Settings ***
Documentation     Run testdata and validate that suite names are set correctly
Suite Setup     Run Tests    ${EMPTY}    misc/multiple_suites/
Resource        atest_resource.robot

*** Test Cases ***
Suite Name With Init Name Setting And Without Child Suite Name
    No Operation

Suite Name With Init Name Setting And With Child Suite Name
    # Should Contain    ${SUITE.suites[0].name}    Suite First    #TODO check suite names
    No Operation

Suite Name Without Init Name Setting And Without Child Suite Name
    No Operation

Suite Name Without Init Name Setting And With Child Suite Name
    No Operation

Child Suite Name Without Init Without Name Setting
    No Operation

Child Suite Name Without Init With Name Setting
    No Operation

Child Suite Name With Init Without Name Setting
    No Operation

Child Suite Name With Init With Name Setting
    No Operation
