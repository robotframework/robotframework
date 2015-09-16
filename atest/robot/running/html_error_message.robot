*** Settings ***
Suite Setup     Run Tests  -l log.html -r report.html  running/html_error_message.robot
Resource        atest_resource.robot

*** Variables ***
${FAILURE}            <a href='http://robotframework.org'>Robot Framework</a>
${MESSAGE}            <b>Hello, world!</b>

*** Test Cases ***
HTML message in log
    ${content} =    Get File   ${OUTDIR}/log.html
    Should Contain Escaped    ${content}    ${FAILURE}
    Should Contain Escaped    ${content}    ${MESSAGE}

HTML message in report
    ${content} =    Get File   ${OUTDIR}/report.html
    Should Contain Escaped    ${content}    ${FAILURE}
    Should Contain Escaped    ${content}    ${MESSAGE}

Failure message in log uses HTML
    ${tc} =    Check Test Case    HTML Failure
    Check Log Message    ${tc.kws[0].msgs[0]}    ${FAILURE}    FAIL    html=True

`Set Test Message` keyword logs using HTML
    ${tc} =    Check Test Case    Set Test Message
    Check Log Message    ${tc.kws[0].msgs[0]}    Set test message to:\n${MESSAGE}    html=True

*** Keywords ***
Should Contain Escaped
    [Arguments]    ${content}    ${expected}
    Should Contain    ${content}    ${expected.replace('</', '\\x3c/')}
