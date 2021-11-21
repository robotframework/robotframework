*** Settings ***
Documentation       Tests for xunit-compatible xml-output.
Resource            atest_resource.robot
Variables           unicode_vars.py
Suite Setup         Run Tests    -x xunit.xml -l log.html --skiponfailure täg    ${TESTDATA}

*** Variables ***
${TESTDATA}         misc/non_ascii.robot
${PASS AND FAIL}    misc/pass_and_fail.robot
${INVALID}          %{TEMPDIR}${/}ïnvälïd-xünït.xml
${XNULL FILE}       xnullish.xml
${NULLISH OPTIONS}
...                 -x ${XNULL FILE} -l log.html --prerebotmodifier NullishStarttimeModifier
${MERGE ONE}        %{TEMPDIR}${/}merge1.xml
${MERGE TWO}        %{TEMPDIR}${/}merge2.xml
${STIME}            20211215-12:11:10.456
${XTIMESTAMP}       2021-12-15T12:11:10.456000
${ETIME}            20211215-12:13:14.789
${OPTIONS WITH TIMES}
...                 --xUnit xunit.xml -l log.html --starttime ${STIME} --endtime ${ETIME}

*** Test Cases ***
XUnit File Is Created
    Stderr should be empty
    Stdout Should Contain    XUnit:
    File Should Exist    ${OUTDIR}/xunit.xml
    File Should Exist    ${OUTDIR}/log.html

File Structure Is Correct
    ${root} =    Get XUnit Node
    Should Be Equal    ${root.tag}    testsuite
    Suite Stats Should Be    ${root}    8    3    1
    ${tests} =    Get XUnit Nodes    testcase
    Length Should Be    ${tests}    8
    ${fails} =    Get XUnit Nodes    testcase/failure
    Length Should Be    ${fails}    3
    Element Attribute Should Be    ${fails}[0]    message
    ...    Setup failed:\n${MESSAGES}
    Element Attribute Should Be    ${fails}[0]    type    AssertionError
    ${skips} =    Get XUnit Nodes    testcase/skipped
    Length Should Be    ${skips}    1
    Element Attribute Should Be    ${skips}[0]    message
    ...    Test failed but its tags matched '--SkipOnFailure' and it was marked skipped.\n\nOriginal failure:\n${MESSAGES}
    Element Attribute Should Be    ${skips}[0]    type    SkipExecution

Non-ASCII Content
    ${tests} =    Get XUnit Nodes    testcase
    Element Attribute Should Be    ${tests}[-1]    name    Ñöñ-ÄŚÇÏÏ Tëśt äņd Këywörd Nämës, Спасибо
    ${failures} =    Get XUnit Nodes    testcase/failure
    Element Attribute Should Be    ${failures}[0]    message    Setup failed:\n${MESSAGES}

Multiline failure
    ${failures} =    Get XUnit Nodes    testcase/failure
    Element Attribute Should Be    ${failures}[-1]    message    Just ASCII here\n\nAlso teardown failed:\n${MESSAGES}

Suite has execution time
    ${suite} =    Get XUnit Node
    Should match    ${suite.attrib['time']}    ?.???
    Should be true    ${suite.attrib['time']} > 0

Test has execution time
    ${test} =    Get XUnit Node    testcase[1]
    Should match    ${test.attrib['time']}    ?.???
    Should be true    ${test.attrib['time']} > 0

Suite has execution timestamp
    Verify Xfile Timestamp    ????-??-??T??:??:??.???000

No XUnit Option Given
    Run Tests    ${EMPTY}    ${TESTDATA}
    Stdout Should Not Contain    XUnit

Invalid XUnit File
    Create Directory    ${INVALID}
    Run Tests    --XUnit ${INVALID} -l log.html    ${TESTDATA}
    File Should Not Exist    ${INVALID}
    File Should Exist    ${OUTDIR}/log.html
    ${dir}    ${base} =    Split Path  ${INVALID}
    ${path} =    Regexp Escape    ${INVALID}
    Stderr Should Match Regexp
    ...    \\[ ERROR \\] Opening xunit file '${path}' failed: .*

Skipping non-critical tests is deprecated
    Run tests    --xUnit xunit.xml --xUnitSkipNonCritical     ${PASS AND FAIL}
    Stderr Should Contain   Command line option --xunitskipnoncritical has been deprecated and has no effect.

Nullish timestamp prerebotmodifier
    Nullish Timestamp Should Be    ${EMPTY}
    
Invalidated suite status
    Run Tests Without Processing Output    -l log.html    ${PASS AND FAIL}
    Remove Suite Status Attribute    ${OUTFILE}    name=starttime
    Execute On Existing Execution Environment
    ...    ${INTERPRETER.rebot}    --xUnit xunit.xml -l log.html    ${OUTFILE}    ${COMMON DEFAULTS}
    Verify Xfile Timestamp    ${EMPTY}

Missing suite status
    Run Tests Without Processing Output    -l log.html    ${PASS AND FAIL}
    Remove Suite Status Element    ${OUTFILE}
    Execute On Existing Execution Environment
    ...    ${INTERPRETER.rebot}    --xUnit xunit.xml -l log.html    ${OUTFILE}    ${COMMON DEFAULTS}
    Verify Xfile Timestamp    ${EMPTY}

Merge outputs
    Run Tests Without Processing Output    --output ${MERGE ONE}    ${PASS AND FAIL}
    Run Tests Without Processing Output    --output ${MERGE TWO}    ${TESTDATA}
    Execute On Existing Execution Environment
    ...    ${INTERPRETER.rebot}    --xUnit xunit.xml -l log.html    ${MERGE TWO} ${MERGE ONE}    ${COMMON DEFAULTS}
    Verify Xfile Timestamp    ${EMPTY}

Merge outputs with times
    Run Tests Without Processing Output    --output ${MERGE ONE}    ${PASS AND FAIL}
    Run Tests Without Processing Output    --output ${MERGE TWO}    ${TESTDATA}
    Execute On Existing Execution Environment
    ...    ${INTERPRETER.rebot}    ${OPTIONS WITH TIMES}    ${MERGE TWO} ${MERGE ONE}    ${COMMON DEFAULTS}
    Verify Xfile Timestamp    ${XTIMESTAMP}

Rebot with start and end time
    Run Tests Without Processing Output    -l log.html    ${PASS AND FAIL}
    Execute On Existing Execution Environment
    ...    ${INTERPRETER.rebot}    ${OPTIONS WITH TIMES}    ${OUTFILE}    ${COMMON DEFAULTS}
    Verify Xfile Timestamp    ${XTIMESTAMP}

*** Keywords ***
Get XUnit Node
    [Arguments]    ${xpath}=.
    ${node} =    Get Element    ${OUTDIR}/xunit.xml    ${xpath}
    [Return]    ${node}

Get XUnit Nodes
    [Arguments]    ${xpath}
    ${nodes} =    Get Elements    ${OUTDIR}/xunit.xml    ${xpath}
    [Return]    ${nodes}

Suite Stats Should Be
    [Arguments]    ${elem}    ${tests}    ${failures}    ${skipped}
    Element Attribute Should Be       ${elem}    tests       ${tests}
    Element Attribute Should Be       ${elem}    failures    ${failures}
    Element Attribute Should Be       ${elem}    skipped     ${skipped}
    Element Attribute Should Match    ${elem}    time        ?.???
    Element Attribute Should Be       ${elem}    errors      0
    Element Attribute Should Match    ${elem}    timestamp   ????-??-??T??:??:??.???000

Nullish Timestamp Should Be
    [Arguments]    ${expected}
    FOR    ${label}    IN    empty    none
        Run Tests    ${NULLISH OPTIONS}:${label}    ${PASS AND FAIL}
        File Should Exist    ${OUTDIR}/${XNULL FILE}
        ${suite} =    Get Element    ${OUTDIR}/${XNULL FILE}    xpath=.
        Should match    ${suite.attrib['timestamp']}    ${expected}
    END

Remove Suite Status Attribute
    [Arguments]    ${source}    ${name}
    ${xml} =    Parse Xml    ${source}
    Remove Element Attribute    ${xml}    ${name}    xpath=suite/status
    Save Xml    ${xml}    ${source}

Remove Suite Status Element
    [Arguments]    ${source}
    ${xml} =    Parse Xml    ${source}
    Remove Element    ${xml}    xpath=suite/status
    Save Xml    ${xml}    ${source}

Verify Xfile Timestamp
    [Arguments]    ${pattern}
    File Should Exist    ${OUTDIR}/xunit.xml
    ${suite} =    Get XUnit Node
    Should match    ${suite.attrib['timestamp']}    ${pattern}
