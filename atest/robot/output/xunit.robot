*** Settings ***
Documentation       Tests for xunit-compatible xml-output.
Resource            atest_resource.robot
Variables           unicode_vars.py
Suite Setup         Run Tests    -x xunit.xml -l log.html --skiponfailure täg    ${TESTDATA}

*** Variables ***
${TESTDATA}         misc/non_ascii.robot
${PASS AND FAIL}    misc/pass_and_fail.robot
${INVALID}          %{TEMPDIR}${/}ïnvälïd-xünït.xml

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
