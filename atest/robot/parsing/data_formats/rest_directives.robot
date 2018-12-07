*** Settings ***
Force Tags      require-docutils
Resource        formats_resource.robot

*** Test Cases ***
One ReST using code-directive
    Run sample file and check tests    ${EMPTY}    ${RESTDIR2}/sample.rst

ReST With ReST Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

Parsing reST files automatically is deprecated
    Previous Run Should Have Been Successful
    Check Automatic Parsing Deprecated Message    0    ${RESTDIR2}/sample.rst
    Length should be    ${ERRORS}    1

Using --extension avoids deprecation warning
    Run sample file and check tests    --extension rst    ${RESTDIR2}/sample.rst
    Length should be    ${ERRORS}    0
