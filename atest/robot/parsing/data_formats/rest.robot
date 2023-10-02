*** Settings ***
Force Tags      require-docutils
Resource        formats_resource.robot

*** Test Cases ***
One reST using code-directive
    Run sample file and check tests    ${EMPTY}    ${RESTDIR}/sample.rst

ReST With reST Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

Parsing errors have correct source
    Previous Run Should Have Been Successful
    Error in file    0    ${RESTDIR}/sample.rst    14
    ...   Non-existing setting 'Invalid'.
    Error in file    1    ${RESTDIR}/../resources/rest_directive_resource.rst    3
    ...   Non-existing setting 'Invalid Resource'.
    Length should be    ${ERRORS}    2

ReST Directory
    Run Suite Dir And Check Results    -F rst:rest    ${RESTDIR}

Directory With reST Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}

Parsing errors in init file have correct source
    Previous Run Should Have Been Successful
    Error in file    0    ${RESTDIR}/sample.rst    14
    ...   Non-existing setting 'Invalid'.
    Error in file    1    ${RESTDIR}/with_init/__init__.rst    4
    ...   Non-existing setting 'Invalid Init'.
    Error in file    2    ${RESTDIR}/../resources/rest_directive_resource.rst    3
    ...   Non-existing setting 'Invalid Resource'.
    Length should be    ${ERRORS}    3

'.robot.rst' files are parsed automatically
    Run Tests    ${EMPTY}    ${RESTDIR}/with_init
    Should Be Equal    ${SUITE.name}    With Init
    Should Be Equal    ${SUITE.suites[0].name}    Sub Suite2
    Should Contain Tests    ${SUITE}    Suite2 Test
