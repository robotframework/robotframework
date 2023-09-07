*** Settings ***
Suite Setup       Run Tests And Read Outputs
Suite Teardown    Remove Files    ${INFILE1}    ${INFILE2}
Resource          atest_resource.robot

*** Variables ***
${INFILE1}        %{TEMPDIR}${/}rebot-test-1.xml
${INFILE2}        %{TEMPDIR}${/}rebot-test-2.xml

*** Test Cases ***
Tags Defined With Robot Set Tag Should Be Preserved
    Run Rebot    \    ${INFILE1}
    Check Test Tags    First One    f1    robottag    t1    t2

Process One File Using Set Tag
    Run Rebot    --settag rebottag    ${INFILE1}
    Check Test Tags    First One    f1    rebottag    robottag    t1    t2

Process One File Using Set Tag With Previously Defined Tag
    Run Rebot    --settag f1    ${INFILE1}
    Check Test Tags    First One    f1    robottag    t1    t2

Process One File Using Set Tag Multiple Times
    Run Rebot    --settag rebottag --settag RebotTag2    ${INFILE1}
    Check Test Tags    First One    f1    rebottag    RebotTag2    robottag    t1
    ...    t2

Process Multiple Files Using set Tag
    Run Rebot    --settag rebottag    ${INFILE1} ${INFILE2}
    Check Test Tags    First One    f1    rebottag    robottag    t1    t2
    Check Test Tags    SubSuite1 First    f1    rebottag    t1

*** Keywords ***
Run Tests And Read Outputs
    Run Tests Without Processing Output    --settag robottag    misc${/}normal.robot
    Move File    ${OUT_FILE}    ${INFILE1}
    Run Tests Without Processing Output    \    misc${/}suites${/}subsuites
    Move File    ${OUT_FILE}    ${INFILE2}
