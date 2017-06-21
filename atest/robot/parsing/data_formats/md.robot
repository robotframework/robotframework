*** Settings ***
Force Tags      markdown_tests
Resource        formats_resource.robot

*** Test Cases ***
One MD
    Run sample file and check tests  ${MDDIR}${/}sample.md
    Stderr should be empty

MD With MD Resource
    Previous Run Should Have Been Successful
    Check Test Case  Resource File
    Stderr should be empty

MD Directory
    Run Suite Dir And Check Results  ${MDDIR}
    Stderr should be empty

Directory With MD Init
    Previous Run Should Have Been Successful
    Check Suite With Init  ${SUITE.suites[1]}
    Stderr should be empty
