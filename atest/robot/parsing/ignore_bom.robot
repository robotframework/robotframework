*** Settings ***
Documentation  Verify that byte order mark (BOM) is igored in TXT and TSV files
Suite Setup    Run Tests  --include bomelo  parsing/bom.tsv parsing/bom.robot
Resource       atest_resource.robot

*** Test Cases ***
Byte order mark in plain text file
    [Setup]    File Should Have Bom    parsing/bom.robot
    ${tc} =    Check test case  ${TESTNAME}
    Check log message    ${tc.kws[0].msgs[0]}    Hyvää päivää €åppa!

Byte order mark in TSV file
    [Setup]    File Should Have Bom    parsing/bom.robot
    ${tc} =    Check test case  ${TESTNAME}
    Check log message    ${tc.kws[0].msgs[0]}    Hyvää päivää €åppa!

*** Keywords ***
File Should Have Bom
    [Arguments]    ${path}
    ${content} =    Get File    ${DATADIR}/${path}
    Should Start With    ${content}    \ufeff    No BOM!!
