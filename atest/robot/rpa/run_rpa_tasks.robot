*** Settings ***
Test Template     Run and validate RPA tasks
Resource          atest_resource.robot

*** Test Cases ***
Task header
    ${EMPTY}      rpa/tasks1.robot                     Task

Task header in multiple files
    ${EMPTY}      rpa/tasks1.robot rpa/tasks2.robot    Task    Failing    Passing

Task header in directory
    ${EMPTY}      rpa/tasks                            Task    Another task

Test header with --rpa
    --rpa         rpa/tests.robot                      Test

Task header with --norpa
    [Template]    Run and validate test cases
    --norpa       rpa/tasks                            Task    Another task

Conflickting headers cause error
    [Template]    Run and validate conflict
    rpa/tests.robot rpa/tasks     rpa/tasks/stuff.robot    tasks    tests
    rpa/                          rpa/tests.robot          tests    tasks

Conflickting headers with --rpa are fine
    --RPA       rpa/tasks rpa/tests.robot    Task    Another task    Test

Conflickting headers with --norpa are fine
    [Template]    Run and validate test cases
    --NorPA     rpa/    Task    Another task    Task    Failing    Passing    Test

--task as alias for --test
    --task task                            rpa/tasks    Task
    --rpa --task Test --test "An* T???"    rpa/         Another task    Test

*** Keywords ***
Run and validate RPA tasks
    [Arguments]    ${options}    ${sources}    @{tasks}
    Run tests     --log log --report report ${options}   ${sources}
    Element attribute should be    ${OUTDIR}/output.xml     rpa    true
    File should contain regexp     ${OUTDIR}/log.html       window.settings = \\{.*"rpa":true,.*\\};
    File should contain regexp     ${OUTDIR}/report.html    window.settings = \\{.*"rpa":true,.*\\};
    Should contain tests    ${SUITE}    @{tasks}

Run and validate test cases
    [Arguments]    ${options}    ${sources}    @{tasks}
    Run tests     --log log --report report ${options}   ${sources}
    Element attribute should be    ${OUTDIR}/output.xml     rpa    false
    File should contain regexp     ${OUTDIR}/log.html       window.settings = \\{.*"rpa":false,.*\\};
    File should contain regexp     ${OUTDIR}/report.html    window.settings = \\{.*"rpa":false,.*\\};
    Should contain tests    ${SUITE}    @{tasks}

Run and validate conflict
    [Arguments]    ${paths}    ${conflicting}    ${this}    ${that}
    Run tests without processing output    ${EMPTY}    ${paths}
    ${conflicting} =    Normalize path    ${DATADIR}/${conflicting}
    ${message} =    Catenate
    ...    [ ERROR ] Conflicting execution modes.
    ...    File '${conflicting}' has ${this} but files parsed earlier have ${that}.
    ...    Fix headers or use '--rpa' or '--norpa' options to set the execution mode explicitly.
    Stderr Should Be Equal To    ${message}${USAGE TIP}\n
