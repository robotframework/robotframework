*** Settings ***
Suite Setup     Run tests    -l LOG -r RaP    misc/multiple_suites/suiTe_8.robot
Resource        atest_resource.robot

*** Test Cases ***
Suite name is not case normalized
    Should Be Equal    ${SUITE.name}    suiTe 8

Suite source should not be case normalized
    Should Be True    str($SUITE.source).endswith(r'multiple_suites${/}suiTe_8.robot')

Outputs are not case normalized
    Stdout Should Contain    ${/}LOG.html
    Stdout Should Contain    ${/}RaP.html
