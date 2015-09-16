*** Settings ***
Documentation   Tests for xunit-compatible xml-output.
Resource        atest_resource.robot
Variables       unicode_vars.py
Suite Setup     Run Tests  -x xunit.xml -l log.html  ${TESTDATA}

*** Variables ***
${TESTDATA}  misc/unicode.robot
${PASS AND FAIL}  misc/pass_and_fail.robot
${INVALID}   %{TEMPDIR}${/}ïnvälïd-xünït.xml

*** Test Cases ***
XUnit File Is Created
    Stderr should be empty
    Check Stdout Contains  XUnit:
    File Should Exist  ${OUTDIR}/xunit.xml
    File Should Exist  ${OUTDIR}/log.html

File Structure Is Correct
    ${root} =  Get XUnit Node
    Should Be Equal  ${root.tag}  testsuite
    Stats Should Be    ${root}    8    4    0
    ${tests} =  Get XUnit Nodes  testcase
    Length Should Be  ${tests}  8
    ${failures} =  Get XUnit Nodes  testcase/failure
    Length Should Be  ${failures}  4

Non-ASCII Content
    ${tests} =  Get XUnit Nodes  testcase
    Should Be Equal  ${tests[-1].attrib['name']}  Ünïcödë Tëst änd Këywörd Nämës
    ${failures} =  Get XUnit Nodes  testcase/failure
    Should Be Equal  ${failures[0].attrib['message']}  ${MESSAGES}

Multiline failure
    ${failures} =  Get XUnit Nodes  testcase/failure
    Should Be Equal  ${failures[-1].attrib['message']}  Just ASCII here\n\nAlso teardown failed:\n${MESSAGES}

No XUnit Option Given
    Run Tests  ${EMPTY}  ${TESTDATA}
    Check Stdout Does Not Contain  XUnit

Invalid XUnit File
    Create Directory  ${INVALID}
    Run Tests  --XUnit ${INVALID} -l log.html  ${TESTDATA}
    File Should Not Exist  ${INVALID}
    File Should Exist  ${OUTDIR}/log.html
    ${dir}  ${base} =  Split Path  ${INVALID}
    ${path} =  Regexp Escape  ${INVALID}
    Check Stderr Matches Regexp
    ...  \\[ ERROR \\] Writing xunit file '${path}' failed: .*

Skipping non-critical tests
    Run tests    --xUnit xunit.xml --xUnitSkipNonCritical --NonCritical fail    ${PASS AND FAIL}
    ${root} =    Get XUnit Node  .
    Stats Should Be    ${root}    2    0    1
    ${skipped} =  Get XUnit Node  testcase/skipped
    Should be equal  ${skipped.text}  FAIL: Expected failure

Skipping all tests
    Run tests    --xunit xunit.xml --noncritical force --xunitskip    ${PASS AND FAIL}
    ${root} =  Get XUnit Node  .
    Stats Should Be    ${root}    2    0    2
    ${skipped} =  Get XUnit Nodes  testcase/skipped
    Should be equal  ${skipped[0].text}  PASS
    Should be equal  ${skipped[1].text}  FAIL: Expected failure
    Length Should Be    ${skipped}    2

*** Keywords ***
Get XUnit Node
    [Arguments]  ${xpath}=.
    ${node} =  Get Element  ${OUTDIR}/xunit.xml  ${xpath}
    [Return]  ${node}

Get XUnit Nodes
    [Arguments]  ${xpath}
    ${nodes} =  Get Elements  ${OUTDIR}/xunit.xml  ${xpath}
    [Return]  ${nodes}

Stats Should Be
    [Arguments]    ${elem}    ${tests}    ${failures}    ${skip}
    Element Attribute Should Be    ${elem}    tests       ${tests}
    Element Attribute Should Be    ${elem}    failures    ${failures}
    Element Attribute Should Be    ${elem}    skip        ${skip}
    Element Attribute Should Be    ${elem}    errors      0
