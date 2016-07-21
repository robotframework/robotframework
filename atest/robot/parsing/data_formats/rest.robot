*** Settings ***
Force Tags      require-docutils
Resource        formats_resource.robot

*** Test Cases ***
One ReST
    Run sample file and check tests  ${RESTDIR}${/}sample.rst
    Stderr should be empty

ReST With ReST Resource
    Previous Run Should Have Been Successful
    Check Test Case  Resource File
    Stderr should be empty

ReST Directory
    Run Suite Dir And Check Results  ${RESTDIR}
    Stderr should be empty

Directory With ReST Init
    Previous Run Should Have Been Successful
    Check Suite With Init  ${SUITE.suites[1]}
    Stderr should be empty
