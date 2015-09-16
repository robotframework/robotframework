*** Settings ***
Force Tags      regression    require-docutils
Resource        formats_resource.robot

*** Test Cases ***
One ReST
    Run sample file and check tests  ${RESTDIR}${/}sample.rst

ReST With ReST Resource
    Previous Run Should Have Been Successful
    Check Test Case  Resource File

ReST Directory
    Run Suite Dir And Check Results  ${RESTDIR}

Directory With ReST Init
    Previous Run Should Have Been Successful
    Check Suite With Init  ${SUITE.suites[1]}

