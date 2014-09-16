*** Settings ***
Force Tags      regression    pybot    jybot
Suite Setup     Run tests    -l LOG -r RaP    misc/multiple_suites/suiTe_8.robot
Resource        atest_resource.robot

*** Test Cases ***
Suite name is not case normalized
    Should Be Equal    ${SUITE.name}    suiTe 8

Suite source should not be case normalized
    Should End With    ${SUITE.source}    multiple_suites${/}suiTe_8.robot

Outputs are not case normalized
    Check stdout contains    ${/}LOG.html
    Check stdout contains    ${/}RaP.html
