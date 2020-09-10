*** Settings ***
Suite Setup       Initialize tests and tasks data
Suite Teardown    Purge tests and tasks data
Test Template     Run and validate RPA tasks
Resource          atest_resource.robot

*** Variables ***
@{ALL TASKS}      Task    Another task    Task    Failing    Passing    Test
...               Defaults    Override    Task timeout exceeded    Invalid task timeout

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
    ...    [[] ERROR ] Error in file '*[/\\]task_setup_teardown_template_timeout.robot' on line 6:
    ...    Non-existing setting 'Tesk Setup'. Did you mean:\n
    ...    ${SPACE*3}Test Setup\n
    ...    ${SPACE*3}Task Setup\n

Conflicting headers with --rpa are fine
    --RPA       rpa/tasks rpa/tests.robot    Task    Another task    Test

Conflicting headers with --norpa are fine
    [Template]    Run and validate test cases
    --NorPA -v TIMEOUT:Test    rpa/    @{ALL TASKS}

Conflicting headers in same file cause error
    [Documentation]    Using --rpa or --norpa doesn't affect the behavior.
    [Template]    NONE
    ${result}=    Run tests without processing output    --rpa    %{TEMPDIR}/rpa/tasks_and_tests.robot
    Should be equal    ${result.rc}    ${252}
    ${path} =    Normalize path    %{TEMPDIR}/rpa/tasks_and_tests.robot
    ${message} =    Catenate
    ...    [ ERROR ] Parsing '${path}' failed:
    ...    One file cannot have both tests and tasks.
    Stderr Should Be Equal To    ${message}${USAGE TIP}\n

Conflicting headers in same file cause error when executing directory
    [Template]    NONE
    ${result}=    Run tests without processing output   ${EMPTY}    %{TEMPDIR}/rpa/
    Should be equal    ${result.rc}    ${252}
    ${path} =    Normalize path    %{TEMPDIR}/rpa/tasks_and_tests.robot
    ${message} =    Catenate
        ...    [ ERROR ] Parsing '${path}' failed:
        ...    One file cannot have both tests and tasks.
    Stderr Should Be Equal To    ${message}${USAGE TIP}\n

--task as alias for --test
    --task task                            rpa/tasks    Task
    --rpa --task Test --test "An* T???"    rpa/         Another task    Test

Error message is correct if no task match --task or other options
    [Template]    Run and validate no task found
    --task nonex                   matching name 'nonex'
    --include xxx --exclude yyy    matching tag 'xxx' and not matching tag 'yyy'
    --suite nonex --task task      matching name 'task' in suite 'nonex'

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
    [Arguments]    ${paths}    ${conflicting}    ${this}    ${that}    @{extra errors}
    Run tests without processing output    ${EMPTY}    ${paths}
    ${conflicting} =    Normalize path    ${DATADIR}/${conflicting}
    ${extra} =    Catenate    @{extra errors}
    ${error} =    Catenate
    ...    [[] ERROR ] Parsing '${conflicting}' failed: Conflicting execution modes.
    ...    File has ${this} but files parsed earlier have ${that}.
    ...    Fix headers or use '--rpa' or '--norpa' options to set the execution mode explicitly.
    Stderr Should Match    ${extra}${error}${USAGE TIP}\n

Run and validate no task found
    [Arguments]    ${options}    ${message}
    Run tests without processing output    --rpa ${options}    rpa/tasks
    Stderr Should Be Equal To    [ ERROR ] Suite 'Tasks' contains no tasks ${message}.${USAGE TIP}\n

Outputs should contain correct mode information
    [Arguments]    ${rpa}
    ${title} =    Set variable if    "${rpa}" == "false"    Test    Task
    ${lower} =    Set variable if    "${rpa}" == "false"    test    task
    Element attribute should be    ${OUTDIR}/output.xml     rpa    ${rpa}
    Element text should be         ${OUTDIR}/output.xml     All ${title}s         xpath=statistics/total/stat[1]
    File should contain regexp     ${OUTDIR}/log.html       window\\.settings = \\{.*"rpa":${rpa},.*\\};
    File should contain regexp     ${OUTDIR}/report.html    window\\.settings = \\{.*"rpa":${rpa},.*\\};
    File should contain regexp     ${OUTDIR}/log.html       window\\.output\\["stats"\\] = \\[\\[\\{.*"label":"All ${title}s",.*\\}\\]\\];
    File should contain regexp     ${OUTDIR}/report.html    window\\.output\\["stats"\\] = \\[\\[\\{.*"label":"All ${title}s",.*\\}\\]\\];
    Stdout Should Contain Regexp    \\d+ ${lower}s?, \\d+ passed, \\d+ failed\n

Initialize tests and tasks data
    Create directory    ${TEMPDIR}/rpa
    Copy file    ${DATADIR}/rpa/_tasks_and_tests.robot    %{TEMPDIR}/rpa/tasks_and_tests.robot
    Copy file    ${DATADIR}/rpa/tasks1.robot              %{TEMPDIR}/rpa/tasks.robot

Purge tests and tasks data
    Remove directory    ${TEMPDIR}/rpa    recursive=True
