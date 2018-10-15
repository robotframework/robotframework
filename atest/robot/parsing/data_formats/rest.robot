*** Settings ***
Force Tags      require-docutils
Resource        formats_resource.robot

*** Test Cases ***
One ReST
    Run sample file and check tests    ${EMPTY}    ${RESTDIR}/sample.rst

ReST With ReST Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

ReST Converted To HTML Is Deprecated
    Previous Run Should Have Been Successful
    Check HTML Deprecation Message    0    ${RESTDIR}/sample.rst
    Check HTML Deprecation Message    2    ${RESOURCEDIR}/rest_resource.rst
    Check HTML Deprecation Message    3    ${RESOURCEDIR}/rest_resource2.rest

Parsing reST files automatically is deprecated
    Previous Run Should Have Been Successful
    Check Automatic Parsing Deprecated Message    1    ${RESTDIR}/sample.rst
    Length should be    ${ERRORS}    4

Using --extension avoids deprecation warning
    Run sample file and check tests    --extension rst    ${RESTDIR}/sample.rst
    Length should be    ${ERRORS}    3

ReST Directory
    Run Suite Dir And Check Results    -F rst:rest    ${RESTDIR}

Directory With ReST Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}
