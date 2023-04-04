*** Settings ***
Resource        atest_resource.robot
Suite Setup     Run Tests    ${EMPTY}    misc/suites/subsuites2

*** Variables ***
${SOURCE}       ${{pathlib.Path(r'${DATADIR}/misc/suites/subsuites2')}}

*** Test Cases ***
Suite source and test lineno in output after execution
    Source info should be correct

Suite source and test lineno in output after Rebot
    Copy Previous Outfile
    Run Rebot    ${EMPTY}    ${OUTFILE COPY}
    Source info should be correct

*** Keywords ***
Source info should be correct
    Should Be Equal    ${SUITE.source}                       ${SOURCE}
    Should Be Equal    ${SUITE.suites[0].source}             ${SOURCE / 'sub.suite.4.robot'}
    Should Be Equal    ${SUITE.suites[0].tests[0].lineno}    ${2}
    Should Be Equal    ${SUITE.suites[1].source}             ${SOURCE / 'subsuite3.robot'}
    Should Be Equal    ${SUITE.suites[1].tests[0].lineno}    ${9}
    Should Be Equal    ${SUITE.suites[1].tests[1].lineno}    ${14}
