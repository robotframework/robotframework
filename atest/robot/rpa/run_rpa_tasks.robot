*** Settings ***
Suite Setup       Initialize tests and tasks data
Suite Teardown    Purge tests and tasks data
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

Conflicting headers cause error
    [Template]    Run and validate conflict
    rpa/tests.robot rpa/tasks     rpa/tasks/stuff.robot    tasks    tests
    rpa/                          rpa/tests.robot          tests    tasks

Conflicting headers with --rpa are fine
    --RPA       rpa/tasks rpa/tests.robot    Task    Another task    Test

Conflicting headers with --norpa are fine
    [Template]    Run and validate test cases
    --NorPA     rpa/    Task    Another task    Task    Failing    Passing    Test

Conflicting headers in same file cause error
    [Documentation]    Using --rpa or --norpa doesn't affect the behavior.
    [Template]    NONE
    Run tests without processing output    --rpa    %{TEMPDIR}/rpa/tasks_and_tests.robot
    ${path} =    Normalize path    %{TEMPDIR}/rpa/tasks_and_tests.robot
    ${message} =    Catenate
    ...    [ ERROR ] Parsing '${path}' failed:
    ...    One file cannot have both tests and tasks.
    Stderr Should Be Equal To    ${message}${USAGE TIP}\n

Conflicting headers in same file cause error when executing directory
    [Template]    NONE
    Run tests    ${EMPTY}    %{TEMPDIR}/rpa/
    Should contain tests    ${SUITE}    Task
    ${path} =    Normalize path    %{TEMPDIR}/rpa/tasks_and_tests.robot
    Check log message    ${ERRORS[0]}    Parsing '${path}' failed: One file cannot have both tests and tasks.    ERROR

--task as alias for --test
    --task task                            rpa/tasks    Task
    --rpa --task Test --test "An* T???"    rpa/         Another task    Test

*** Keywords ***
Run and validate RPA tasks
    [Arguments]    ${options}    ${sources}    @{tasks}
    Run tests     --log log --report report ${options}   ${sources}
    Outputs should contain correct mode information    rpa=true
    Should contain tests    ${SUITE}    @{tasks}

Run and validate test cases
    [Arguments]    ${options}    ${sources}    @{tasks}
    Run tests     --log log --report report ${options}   ${sources}
    Outputs should contain correct mode information    rpa=false
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

Outputs should contain correct mode information
    [Arguments]    ${rpa}
    ${title} =    Set variable if    "${rpa}" == "false"    Test    Task
    ${lower} =    Set variable if    "${rpa}" == "false"    test    task
    Element attribute should be    ${OUTDIR}/output.xml     rpa    ${rpa}
    Element text should be         ${OUTDIR}/output.xml     Critical ${title}s    xpath=statistics/total/stat[1]
    Element text should be         ${OUTDIR}/output.xml     All ${title}s         xpath=statistics/total/stat[2]
    File should contain regexp     ${OUTDIR}/log.html       window\\.settings = \\{.*"rpa":${rpa},.*\\};
    File should contain regexp     ${OUTDIR}/report.html    window\\.settings = \\{.*"rpa":${rpa},.*\\};
    File should contain regexp     ${OUTDIR}/log.html       window\\.output\\["stats"\\] = \\[\\[\\{.*"label":"Critical ${title}s",.*\\}\\]\\];
    File should contain regexp     ${OUTDIR}/report.html    window\\.output\\["stats"\\] = \\[\\[\\{.*"label":"Critical ${title}s",.*\\}\\]\\];
    File should contain regexp     ${OUTDIR}/log.html       window\\.output\\["stats"\\] = \\[\\[\\{.*"label":"All ${title}s",.*\\}\\]\\];
    File should contain regexp     ${OUTDIR}/report.html    window\\.output\\["stats"\\] = \\[\\[\\{.*"label":"All ${title}s",.*\\}\\]\\];
    Check Stdout Contains Regexp    \\d+ critical ${lower}s?, \\d+ passed, \\d+ failed\n\\d+ ${lower}s? total, \\d+ passed, \\d+ failed\n

Initialize tests and tasks data
    Create directory    ${TEMPDIR}/rpa
    Copy file    ${DATADIR}/rpa/_tasks_and_tests.robot    %{TEMPDIR}/rpa/tasks_and_tests.robot
    Copy file    ${DATADIR}/rpa/tasks1.robot              %{TEMPDIR}/rpa/tasks.robot

Purge tests and tasks data
    Remove directory    ${TEMPDIR}/rpa    recursive=True
