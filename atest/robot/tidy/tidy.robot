*** Settings ***
Resource          tidy_resource.robot
Test Setup        Create Directory     ${TEMP}
Test Teardown     Remove Directory     ${TEMP}    recursive=True

*** Test Cases ***
Tidying single test case file
    [Documentation]   Test tidying to different formats
    [Template]    Run tidy with golden file and check result
    ${EMPTY}            golden.robot
    --usepipes -f txt   golden_pipes.robot
    --format tsv        golden.tsv
    --format html       golden.html
    --for robot         golden.robot
    --spacecount 2      golden_two_spaces.robot

Tidying single resource file
    [Template]    Run tidy with golden resource file and check result
    ${EMPTY}    golden_resource.robot
    -p    golden_pipes_resource.robot
    -f tsv    golden_resource.tsv
    --FORMAT html    golden_resource.html
    --FOR ROBOT    golden_resource.robot

Tidying single init file
    Run tidy and check result    ${EMPTY}    __init__.robot
    File Should Exist    ${TEMP FILE}

Tidying single file without output file prints output to console
    [Documentation]    Depending on console encoding, non-ASCII characters may not be shown correctly.
    ${stdout} =    Run tidy    ${EMPTY}    golden.robot    output=None    stderr=False
    Compare tidy results    ${stdout}    golden.robot    \\s+Log Many\\s+Non-ASCII:.*\\s+\\$\\{CURDIR\\}
    File Should Not Exist    ${TEMP FILE}

Default format is got from output file
    Run tidy    ${EMPTY}    ${DATA}/golden.robot    ${TEMP}/golden.html
    Compare tidy results    ${TEMP}/golden.html    ${DATA}/golden.html

Tidying directory
    [Setup]    Copy Directory    ${DATA}/tests    ${TEMP}/tests
    ${result_before}=    Run Tests    sources=${DATA}/tests
    Run Tidy    --recursive --format TSV    ${TEMP}/tests
    Check file count    ${TEMP}/tests    *.tsv    2
    Check file count    ${TEMP}/tests/sub    *.tsv    1
    Check file count    ${TEMP}/tests    *.txt    0
    Check file count    ${TEMP}/tests/sub    *.txt    0
    Files Should Have $CURDIR    ${TEMP}/tests
    Files Should Have $CURDIR    ${TEMP}/tests/sub
    ${result_after}=     Run Tests    sources=${TEMP}/tests
    Should Be Equal    ${result_before.stdout}    ${result_after.stdout}

Custom headers are preserved and tables aligned accordingly
    Run tidy and check result    ${EMPTY}     golden_with_headers.robot

Running Tidy as script
    [Tags]   no-standalone
    Run tidy as script and check result    ${EMPTY}    golden.robot

Tidy tests and keywords containing ELSE and ELSE IF
    [Setup]    Copy File    ${DATA}/else_untidy.robot    ${TEMP}/else_untidy.robot
    Run tidy    --inplace     ${TEMP}/else_untidy.robot
    Compare tidy results    ${TEMP}/else_untidy.robot    ${DATA}/else_tidy.robot

For loops
    Run tidy and check result    ${EMPTY}    for_loops_input.robot
    ...    expected=for_loops_expected.robot

*** Keywords ***
Files Should Have $CURDIR
    [Arguments]    ${directory}
    @{paths} =    List Files In Directory    ${directory}    absolute=True
    FOR    ${path}    IN    @{paths}
        ${content} =    Get File    ${path}
        Should Contain    ${content}    $\{CURDIR}
    END
