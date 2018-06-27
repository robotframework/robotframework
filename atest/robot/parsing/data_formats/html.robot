*** Settings ***
Resource          formats_resource.robot

*** Test Cases ***
One HTML
    Run sample file and check tests    ${EMPTY}    ${HTMLDIR}/sample.html

HTML With HTML Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

HTML Is Deprecated
    Previous Run Should Have Been Successful
    Check HTML Deprecation Message    1    ${HTMLDIR}/sample.html
    Check HTML Deprecation Message    2    ${RESOURCEDIR}/html_resource.html
    Check HTML Deprecation Message    3    ${RESOURCEDIR}/html_resource2.htm
    Length Should Be    ${ERRORS}    4

HTML Directory
    Run Suite Dir And Check Results    ${EMPTY}    ${HTMLDIR}
    ${malformed} =    Normalize Path    ${HTMLDIR}/malformed.html
    Check Syslog Contains    Data source '${malformed}' has no tests or tasks.

Directory With HTML Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}
