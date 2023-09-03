*** Settings ***
Documentation     Running multiple suites together.
Resource          cli_resource.robot

*** Test Cases ***
Default Name
    Run Tests    ${EMPTY}    misc/pass_and_fail.robot misc/normal.robot
    Check Names    ${SUITE}    Pass And Fail & Normal
    Should Contain Suites    ${SUITE}    Pass And Fail    Normal
    Check Names    ${SUITE.suites[0]}    Pass And Fail    Pass And Fail & Normal.
    Should Contain Tests    ${SUITE.suites[0]}    Pass    Fail
    Check Names    ${SUITE.suites[0].tests[0]}    Pass    Pass And Fail & Normal.Pass And Fail.
    Check Names    ${SUITE.suites[0].tests[1]}    Fail    Pass And Fail & Normal.Pass And Fail.
    Check Names    ${SUITE.suites[1]}    Normal    Pass And Fail & Normal.
    Should Contain Tests    ${SUITE.suites[1]}    First One    Second One
    Check Names    ${SUITE.suites[1].tests[0]}    First One    Pass And Fail & Normal.Normal.
    Check Names    ${SUITE.suites[1].tests[1]}    Second One    Pass And Fail & Normal.Normal.

Overridden Name
    Run Tests    --name "My Name"    misc/pass_and_fail.robot misc/normal.robot
    Check Names    ${SUITE}    My Name
    Should Contain Suites    ${SUITE}    Pass And Fail    Normal
    Check Names    ${SUITE.suites[0]}    Pass And Fail    My Name.
    Should Contain Tests    ${SUITE.suites[0]}    Pass    Fail
    Check Names    ${SUITE.suites[0].tests[0]}    Pass    My Name.Pass And Fail.
    Check Names    ${SUITE.suites[0].tests[1]}    Fail    My Name.Pass And Fail.
    Check Names    ${SUITE.suites[1]}    Normal    My Name.
    Should Contain Tests    ${SUITE.suites[1]}    First One    Second One
    Check Names    ${SUITE.suites[1].tests[0]}    First One    My Name.Normal.
    Check Names    ${SUITE.suites[1].tests[1]}    Second One    My Name.Normal.

Wildcards
    Run Tests    ${EMPTY}    misc/suites/tsuite?.*bot
    Check Names    ${SUITE}    Tsuite1 & Tsuite2 & Tsuite3
    Should Contain Suites    ${SUITE}    Tsuite1    Tsuite2    Tsuite3
    Check Names    ${SUITE.suites[0]}    Tsuite1    Tsuite1 & Tsuite2 & Tsuite3.
    Should Contain Tests    ${SUITE.suites[0]}    Suite1 First    Suite1 Second    Third In Suite1
    Check Names    ${SUITE.suites[0].tests[0]}    Suite1 First    Tsuite1 & Tsuite2 & Tsuite3.Tsuite1.
    Check Names    ${SUITE.suites[0].tests[1]}    Suite1 Second    Tsuite1 & Tsuite2 & Tsuite3.Tsuite1.
    Check Names    ${SUITE.suites[0].tests[2]}    Third In Suite1    Tsuite1 & Tsuite2 & Tsuite3.Tsuite1.
    Check Names    ${SUITE.suites[1]}    Tsuite2    Tsuite1 & Tsuite2 & Tsuite3.
    Should Contain Tests    ${SUITE.suites[1]}    Suite2 First
    Check Names    ${SUITE.suites[1].tests[0]}    Suite2 First    Tsuite1 & Tsuite2 & Tsuite3.Tsuite2.
    Check Names    ${SUITE.suites[2]}    Tsuite3    Tsuite1 & Tsuite2 & Tsuite3.
    Should Contain Tests    ${SUITE.suites[2]}    Suite3 First
    Check Names    ${SUITE.suites[2].tests[0]}    Suite3 First    Tsuite1 & Tsuite2 & Tsuite3.Tsuite3.

With Init File Included
    Run Tests    ${EMPTY}    misc/suites/tsuite1.robot misc/suites/tsuite2.robot misc/suites/__init__.robot
    Check Names    ${SUITE}    Tsuite1 & Tsuite2
    Should Contain Suites    ${SUITE}    Tsuite1    Tsuite2
    Check Keyword Data    ${SUITE.teardown}    BuiltIn.Log    args=\${SUITE_TEARDOWN_ARG}    type=TEARDOWN
    Check Names    ${SUITE.suites[0]}    Tsuite1    Tsuite1 & Tsuite2.
    Should Contain Tests    ${SUITE.suites[0]}    Suite1 First    Suite1 Second    Third In Suite1
    Check Names    ${SUITE.suites[0].tests[0]}    Suite1 First    Tsuite1 & Tsuite2.Tsuite1.
    Check Names    ${SUITE.suites[0].tests[1]}    Suite1 Second    Tsuite1 & Tsuite2.Tsuite1.
    Check Names    ${SUITE.suites[0].tests[2]}    Third In Suite1    Tsuite1 & Tsuite2.Tsuite1.
    Check Names    ${SUITE.suites[1]}    Tsuite2    Tsuite1 & Tsuite2.
    Should Contain Tests    ${SUITE.suites[1]}    Suite2 First
    Check Names    ${SUITE.suites[1].tests[0]}    Suite2 First    Tsuite1 & Tsuite2.Tsuite2.

Multiple Init Files Not Allowed
    Run Tests Without Processing Output    ${EMPTY}    misc/suites/tsuite1.robot misc/suites/__init__.robot misc/suites/__init__.robot
    Stderr Should Contain    [ ERROR ] Multiple init files not allowed.

Failure When Parsing Any Data Source Fails
    Run Tests Without Processing Output    ${EMPTY}    nönex misc/pass_and_fail.robot
    ${nönex} =    Normalize Path    ${DATADIR}/nönex
    Stderr Should Contain    [ ERROR ] Parsing '${nönex}' failed: File or directory to execute does not exist.
    File Should Not Exist    ${OUTDIR}${/}output.xml

Warnings And Error When Parsing All Data Sources Fail
    Run Tests Without Processing Output    ${EMPTY}    nönex1 nönex2
    ${nönex} =    Normalize Path    ${DATADIR}/nönex
    Stderr Should Contain    [ ERROR ] Parsing '${nönex}1' and '${nönex}2' failed: File or directory to execute does not exist.
