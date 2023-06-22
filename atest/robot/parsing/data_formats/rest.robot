*** Settings ***
Force Tags      require-docutils
Resource        formats_resource.robot

*** Test Cases ***
One reST using code-directive
    Run sample file and check tests    ${EMPTY}    ${RESTDIR}/sample.rst
    Stderr Should Be Empty

ReST With reST Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

ReST Directory
    Run Suite Dir And Check Results    -F rst:rest    ${RESTDIR}

Directory With reST Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}

'.robot.rst' files are parsed automatically
    Run Tests    ${EMPTY}    ${RESTDIR}/with_init
    Should Be Equal    ${SUITE.name}    With Init
    Should Be Equal    ${SUITE.suites[0].name}    Sub Suite2
    Should Contain Tests    ${SUITE}    Suite2 Test
