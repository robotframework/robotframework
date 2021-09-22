*** Settings ***
Resource          tidy_resource.robot
Test Setup        Create Directory     ${TEMP}
Test Teardown     Remove Directory     ${TEMP}    recursive=True

*** Test Cases ***
Tidying single test case file spaces -> spaces
    Run tidy with golden file and check result    ${EMPTY}    golden.robot
    Run tidy with golden file and check result    --spacecount 2    golden_two_spaces.robot

Tidying single test case file spaces -> pipes
    Run tidy with golden file and check result    --usepipes    golden_pipes.robot

Tidying single test case file pipes -> spaces
    Run tidy with golden file and check result   ${EMPTY}    golden.robot    input=pipes-input.robot

Tidying single test case file pipes -> pipes
    Run tidy with golden file and check result    --usepipes    golden_pipes.robot    input=pipes-input.robot

Tidying single resource file
    [Template]    Run tidy with golden resource file and check result
    ${EMPTY}            golden_resource.robot
    -p                  golden_pipes_resource.robot

Tidying single init file
    Run tidy and check result    input=__init__.robot
    File Should Exist    ${OUTFILE}

Tidying single file without output file prints output to console
    [Documentation]    Depending on console encoding, non-ASCII characters may not be shown correctly.
    ${stdout} =    Run tidy    input=golden-input.robot    output=None
    Compare tidy results    ${stdout}    golden.robot    \\s+Log Many\\s+Non-ASCII:.*\\s+\\$\\{CURDIR\\}
    File Should Not Exist    ${OUTFILE}

Default format is got from output file
    Run tidy    input=${DATA}/golden.robot    output=${TEMP}/golden.txt
    Compare tidy results    ${TEMP}/golden.txt    ${DATA}/golden.txt

Tidying directory
    [Setup]    Copy Directory    ${DATA}/tests    ${TEMP}/tests
    ${result_before}=    Run Tests    sources=${DATA}/tests
    Run Tidy    --recursive    ${TEMP}/tests
    Check file count    ${TEMP}/tests    *.robot    2
    Check file count    ${TEMP}/tests/sub    *.robot    1
    Check file count    ${TEMP}/tests    *.txt    0
    Check file count    ${TEMP}/tests/sub    *.txt    0
    Files Should Have $CURDIR    ${TEMP}/tests
    Files Should Have $CURDIR    ${TEMP}/tests/sub
    ${result_after}=     Run Tests    sources=${TEMP}/tests
    Should Be Equal    ${result_before.stdout}    ${result_after.stdout}

Custom headers are preserved and tables aligned accordingly
    Run tidy and check result    input=custom_headers_input.robot    expected=golden_with_headers.robot

Running Tidy as script
    Run tidy as script and check result    input=golden.robot

For loops
    Run tidy and check result    input=for_loops_input.robot
    ...    expected=for_loops_expected.robot

*** Keywords ***
Files Should Have $CURDIR
    [Arguments]    ${directory}
    @{paths} =    List Files In Directory    ${directory}    absolute=True
    FOR    ${path}    IN    @{paths}
        ${content} =    Get File    ${path}
        Should Contain    ${content}    $\{CURDIR}
    END
