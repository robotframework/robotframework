*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  misc/multiple_suites
Resource        atest_resource.robot


*** Test Cases ***
Suites Are Ordered Based On The Prefixes
    Should Contain Suites  ${SUITE}  Suite First  Sub.Suite.1  Suite3  Suite4  Suite5
    ...  Suite10  Suite 6  SUite7  suiTe 8  Suite 9 Name
    Should Contain Suites  ${SUITE.suites[1]}   Suite4  .Sui.te.2.
