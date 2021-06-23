*** Settings ***
Force Tags      require-docutils
Resource        formats_resource.robot

*** Test Cases ***
One reST using code-directive
    Run sample file and check tests    ${EMPTY}    ${RESTDIR}/sample.rst

ReST With reST Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

ReST Directory
    Run Suite Dir And Check Results    -F rst:rest    ${RESTDIR}

Directory With reST Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}
