*** Settings ***
Suite Setup     Run Tests  -l log.html -r report.html  running/html_error_message.robot
Resource        atest_resource.robot

*** Variables ***
${MESSAGE}            <b>Hello, world!</b>
${FAILURE}            <a href='http://robotframework.org'>Robot Framework</a>

*** Test Cases ***
Set Test Message
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Set test message to:\n${MESSAGE}    html=True

HTML failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    ${FAILURE}    FAIL    html=True

HTML failure with non-generic exception
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    ValueError: Invalid <b>value</b>    FAIL    html=True

HTML failure in setup
    Check Test Case    ${TESTNAME}

HTML failure in teardown
    Check Test Case    ${TESTNAME}

Normal failure in body and HTML failure in teardown
    Check Test Case    ${TESTNAME}

HTML failure in body and normal failure teardown
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Should be <b>HTML</b>    FAIL    html=True
    Check Log Message    ${tc.teardown.msgs[0]}    Should NOT be <b>HTML</b>    FAIL    html=False

HTML failure in body and in teardown
    Check Test Case    ${TESTNAME}

Continuable failures
    Check Test Case    ${TESTNAME}

HTML message in log
    ${content} =    Get File   ${OUTDIR}/log.html
    Should Contain Escaped    ${content}    ${MESSAGE}
    Should Contain Escaped    ${content}    ${FAILURE}
    Should Contain Escaped    ${content}    Should be <b>HTML</b>
    Should Contain Escaped    ${content}    Should NOT be &lt;b&gt;HTML&lt;/b&gt;
    Should Not Contain        ${content}    Should NOT be <

HTML message in report
    ${content} =    Get File   ${OUTDIR}/report.html
    Should Contain Escaped    ${content}    ${MESSAGE}
    Should Contain Escaped    ${content}    ${FAILURE}
    Should Contain Escaped    ${content}    Should be <b>HTML</b>
    Should Contain Escaped    ${content}    Should NOT be &lt;b&gt;HTML&lt;/b&gt;
    Should Not Contain        ${content}    Should NOT be <

*** Keywords ***
Should Contain Escaped
    [Arguments]    ${content}    ${expected}
    Should Contain    ${content}    ${expected.replace('</', '\\x3c/')}
