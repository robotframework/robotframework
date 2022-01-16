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
    Stderr should be empty
    Stdout Should Contain    XUnit:
    File Should Exist    ${OUTDIR}/xunit.xml
    File Should Exist    ${OUTDIR}/log.html

File Structure Is Correct
    ${root} =    Get XUnit Node
    Should Be Equal    ${root.tag}    testsuite
    Suite Stats Should Be    ${root}    8    3    1    ${SUITE.starttime}
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

XUnit File From Nested Suites
    Run Tests    -x xunit.xml -l log.html    ${TESTDATA} ${NESTED}
    Stderr Should Be Empty
    Stdout Should Contain    XUnit:
    File Should Exist    ${OUTDIR}/xunit.xml
    File Should Exist    ${OUTDIR}/log.html
    ${root} =    Parse XML    ${OUTDIR}/xunit.xml
    Should Be Equal    ${root.tag}    testsuite
    ${suites} =    Get Elements    ${root}    testsuite
    Length Should Be    ${suites}    2
    ${tests} =    Get Elements    ${suites}[0]    testcase
    Length Should Be    ${tests}    8
    Element Attribute Should be    ${tests}[7]    name    Ñöñ-ÄŚÇÏÏ Tëśt äņd Këywörd Nämës, Спасибо
    ${failures} =    Get Elements    ${suites}[0]    testcase/failure
    Length Should Be    ${failures}    4
    Element Attribute Should be    ${failures}[0]    message    ${MESSAGES}
    ${nested suite} =    Get Element    ${OUTDIR}/xunit.xml    xpath=testsuite[2]
    Element Attribute Should Be       ${nested suite}    tests       11
    Element Attribute Should Be       ${nested suite}    failures    1
    ${properties} =    Get Elements    ${nested suite}    testsuite[6]/properties/property
    Length Should Be    ${properties}    2
    Element Attribute Should be    ${properties}[0]    name     Suite Documentation
    Element Attribute Should be    ${properties}[0]    value    Normal test cases
    Element Attribute Should be    ${properties}[1]    name     Something
    Element Attribute Should be    ${properties}[1]    value    My Value

XUnit File Properties
    Run Tests    -M METACLI:"meta CLI" -x xunit.xml -l log.html -v META_VALUE_FROM_CLI:"cli meta"    ${NORMAL SUITE} ${METADATA SUITE}
    Stderr Should Be Empty
    Stdout Should Contain    XUnit:
    File Should Exist    ${OUTDIR}/xunit.xml
    File Should Exist    ${OUTDIR}/log.html
    ${root} =    Parse XML    ${OUTDIR}/xunit.xml
    Should Be Equal    ${root.tag}    testsuite
    # root testsuite has metadata from CLI
    ${root_properties_element} =    Get Elements    ${root}    properties
    Length Should Be    ${root_properties_element}    1
    ${property_elements} =    Get Elements    ${root_properties_element}[0]    property
    Length Should Be    ${property_elements}    1
    Element Attribute Should be    ${property_elements}[0]    name     METACLI
    Element Attribute Should be    ${property_elements}[0]    value    meta CLI
    # suites have their own metadata and suite documentation
    ${suites} =    Get Elements    ${root}    testsuite
    Length Should Be    ${suites}    2
    # normal suite
    ${normal_properties_element} =    Get Elements    ${suites}[0]    properties
    Length Should Be    ${normal_properties_element}    1
    ${property_elements} =    Get Elements    ${normal_properties_element}[0]    property
    Length Should Be    ${property_elements}    2
    Element Attribute Should be    ${property_elements}[0]    name     Suite Documentation
    Element Attribute Should be    ${property_elements}[0]    value    Normal test cases
    # metadata suite
    ${meta_properties_element} =    Get Elements    ${suites}[1]    properties
    Length Should Be    ${meta_properties_element}    1
    ${property_elements} =    Get Elements    ${meta_properties_element}[0]    property
    Length Should Be    ${property_elements}    8
    Element Attribute Should be    ${property_elements}[0]    name     Escaping
    Element Attribute Should be    ${property_elements}[0]    value    Three backslashes \\\\\\\ & \${version}
    Element Attribute Should be    ${property_elements}[1]    name     Multiple columns
    Element Attribute Should be    ${property_elements}[1]    value    Value in multiple columns
    Element Attribute Should be    ${property_elements}[2]    name     multiple lines
    Element Attribute Should be    ${property_elements}[2]    value    Metadata in multiple lines\nis parsed using\nsame semantics as documentation.\n| table |\n| ! |
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
    [Return]    ${node}

Get XUnit Nodes
    [Arguments]    ${xpath}
    ${nodes} =    Get Elements    ${OUTDIR}/xunit.xml    ${xpath}
    [Return]    ${nodes}

Suite Stats Should Be
    [Arguments]    ${elem}    ${tests}    ${failures}    ${skipped}    ${starttime}
    Element Attribute Should Be       ${elem}    tests       ${tests}
    Element Attribute Should Be       ${elem}    failures    ${failures}
    Element Attribute Should Be       ${elem}    skipped     ${skipped}
    Element Attribute Should Match    ${elem}    time        ?.???
    Element Attribute Should Be       ${elem}    errors      0
    Element Attribute Should Be       ${elem}    timestamp
    ...    ${{datetime.datetime.strptime($starttime, '%Y%m%d %H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S.%f')}}
