*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  misc/multiple_suites
Resource        atest_resource.robot
Documentation   Giving suite names from commandline is tested in robot/cli/runner/suite_name_doc_and_metadata.txt


*** Test Cases ***
Root Directory Suite Name
    Should Be Equal  ${SUITE.name}  Multiple Suites

Prefix Is Removed From File Suite Name
    Should Be Equal  ${SUITE.suites[0].name}  Suite First

Prefix Is Removed From Directory Suite Name
    Should Be Equal  ${SUITE.suites[1].name}  Sub.Suite.1

Child File Suite Name
    Should Be Equal  ${SUITE.suites[6].name}  Suite 6

Child Directory Suite Name
    Should Be Equal  ${SUITE.suites[1].name}  Sub.Suite.1

Dots in suite names
    Should Be Equal  ${SUITE.suites[1].name}  Sub.Suite.1
    Should Be Equal  ${SUITE.suites[1].suites[1].name}  .Sui.te.2.

Names without uppercase chars are titlecased
    Should Be Equal  ${SUITE.suites[1].name}  Sub.Suite.1
    Should Be Equal  ${SUITE.suites[6].name}  Suite 6
    Should Be Equal  ${SUITE.suites[9].name}  Suite 9 Name

Names with uppercase chars are not titlecased
    Should Be Equal  ${SUITE.suites[7].name}  SUite7
    Should Be Equal  ${SUITE.suites[8].name}  suiTe 8
    Should Be Equal  ${SUITE.suites[1].suites[1].name}  .Sui.te.2.

Underscores are converted to spaces
    Should Be Equal  ${SUITE.suites[8].name}  suiTe 8
    Should Be Equal  ${SUITE.suites[9].name}  Suite 9 Name

Spaces are preserved
    Should Be Equal  ${SUITE.suites[6].name}  Suite 6

Root File Suite Name
    [Setup]  Run Tests  ${EMPTY}  misc/pass_and_fail.robot
    Should Be Equal  ${SUITE.name}  Pass And Fail

