*** Settings ***
Documentation       Tests for xunit-compatible xml-output.
Resource            atest_resource.robot
Variables           unicode_vars.py
Suite Setup         Run Tests    -x xunit.xml -l log.html --skiponfailure täg    ${TESTDATA}

*** Variables ***
${TESTDATA}         misc/non_ascii.robot
${PASS AND FAIL}    misc/pass_and_fail.robot
${INVALID}          %{TEMPDIR}${/}ïnvälïd-xünït.xml
${NESTED}           misc/suites
${METADATA SUITE}   parsing/suite_metadata.robot
${NORMAL SUITE}     misc/normal.robot

*** Test Cases ***
XUnit File Is Created
    Verify Outputs

File Structure Is Correct
    ${root} =    Get Root Node
    Suite Stats Should Be    ${root}    8    3    1    ${SUITE.start_time}
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
    ...    Test failed but skip-on-failure mode was active and it was marked skipped.\n\nOriginal failure:\n${MESSAGES}
    Element Attribute Should Be    ${skips}[0]    type    SkipExecution
    Element Should Not Exist    ${root}    testsuite/properties

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

XUnit File From Nested Suites
    Run Tests    -x xunit.xml -l log.html    ${TESTDATA} ${NESTED}
    Verify Outputs
    ${root} =    Get Root Node
    ${suites} =    Get Elements    ${root}    testsuite
    Length Should Be    ${suites}    2
    ${tests} =    Get Elements    ${suites}[0]    testcase
    Length Should Be    ${tests}    8
    Element Attribute Should be    ${tests}[7]    name    Ñöñ-ÄŚÇÏÏ Tëśt äņd Këywörd Nämës, Спасибо
    ${failures} =    Get Elements    ${suites}[0]    testcase/failure
    Length Should Be    ${failures}    4
    Element Attribute Should be    ${failures}[0]    message    ${MESSAGES}
    ${nested suite} =    Get Element    ${OUTDIR}/xunit.xml    xpath=testsuite[2]
    Element Attribute Should Be       ${nested suite}    tests       13
    Element Attribute Should Be       ${nested suite}    failures    1
    ${properties} =    Get Elements    ${nested suite}    testsuite[6]/properties/property
    Length Should Be    ${properties}    2
    Element Attribute Should be    ${properties}[0]    name     Documentation
    Element Attribute Should be    ${properties}[0]    value    Normal test cases
    Element Attribute Should be    ${properties}[1]    name     Something
    Element Attribute Should be    ${properties}[1]    value    My Value

XUnit File Root Testsuite Properties From CLI
    Run Tests    -M METACLI:"meta CLI" -x xunit.xml -l log.html -v META_VALUE_FROM_CLI:"cli meta"    ${NORMAL SUITE} ${METADATA SUITE}
    Verify Outputs
    ${root} =    Get Root Node
    ${root_properties_element} =    Get Properties Node    ${root}
    ${property_elements} =    Get Elements    ${root_properties_element}[0]    property
    Length Should Be    ${property_elements}    1
    Element Attribute Should be    ${property_elements}[0]    name     METACLI
    Element Attribute Should be    ${property_elements}[0]    value    meta CLI

XUnit File Testsuite Properties From Suite Documentation
    ${root} =    Get Root Node
    ${suites} =    Get Elements    ${root}    testsuite
    Length Should Be    ${suites}    2
    ${normal_properties_element} =    Get Properties Node    ${suites}[0]
    ${property_elements} =    Get Elements    ${normal_properties_element}[0]    property
    Length Should Be    ${property_elements}    2
    Element Attribute Should be    ${property_elements}[0]    name     Documentation
    Element Attribute Should be    ${property_elements}[0]    value    Normal test cases

XUnit File Testsuite Properties From Metadata
    ${root} =    Get Root Node
    ${suites} =    Get Elements    ${root}    testsuite
    ${meta_properties_element} =    Get Properties Node    ${suites}[1]
    ${property_elements} =    Get Elements    ${meta_properties_element}[0]    property
    Length Should Be    ${property_elements}    8
    Element Attribute Should be    ${property_elements}[0]    name     Escaping
    Element Attribute Should be    ${property_elements}[0]    value    Three backslashes \\\\\\\ & \${version}
    Element Attribute Should be    ${property_elements}[1]    name     Multiple columns
    Element Attribute Should be    ${property_elements}[1]    value    Value in${SPACE*4}multiple${SPACE*4}columns
    Element Attribute Should be    ${property_elements}[2]    name     multiple lines
    Element Attribute Should be    ${property_elements}[2]    value    Metadata in multiple lines\nis parsed using\nsame semantics${SPACE*4}as${SPACE*4}documentation.\n| table |\n|${SPACE*3}!${SPACE*3}|
    Element Attribute Should be    ${property_elements}[3]    name     Name
    Element Attribute Should be    ${property_elements}[3]    value    Value
    Element Attribute Should be    ${property_elements}[4]    name     Overridden
    Element Attribute Should be    ${property_elements}[4]    value    This overrides first value
    Element Attribute Should be    ${property_elements}[5]    name     Value from CLI
    Element Attribute Should be    ${property_elements}[5]    value    cli meta
    Element Attribute Should be    ${property_elements}[6]    name     Variable from resource
    Element Attribute Should be    ${property_elements}[6]    value    Variable from a resource file
    Element Attribute Should be    ${property_elements}[7]    name     variables
    Element Attribute Should be    ${property_elements}[7]    value    Version: 1.2

*** Keywords ***
Get XUnit Node
    [Arguments]    ${xpath}=.
    ${node} =    Get Element    ${OUTDIR}/xunit.xml    ${xpath}
    RETURN    ${node}

Get XUnit Nodes
    [Arguments]    ${xpath}
    ${nodes} =    Get Elements    ${OUTDIR}/xunit.xml    ${xpath}
    RETURN    ${nodes}

Suite Stats Should Be
    [Arguments]    ${elem}    ${tests}    ${failures}    ${skipped}    ${start_time}
    Element Attribute Should Be       ${elem}    tests       ${tests}
    Element Attribute Should Be       ${elem}    failures    ${failures}
    Element Attribute Should Be       ${elem}    skipped     ${skipped}
    Element Attribute Should Match    ${elem}    time        ?.???
    Element Attribute Should Be       ${elem}    errors      0
    Element Attribute Should Be       ${elem}    timestamp   ${start_time.isoformat()}

Verify Outputs
    Stderr should be empty
    Stdout Should Contain    XUnit:
    File Should Exist    ${OUTDIR}/xunit.xml
    File Should Exist    ${OUTDIR}/log.html

Get Root Node
    ${root} =    Get XUnit Node
    Should Be Equal    ${root.tag}    testsuite
    RETURN    ${root}

Get Properties Node
    [Arguments]    ${source}
    ${properties} =    Get Elements    ${source}    properties
    Length Should Be    ${properties}    1
    RETURN    ${properties}
