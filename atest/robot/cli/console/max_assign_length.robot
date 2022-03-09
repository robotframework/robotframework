*** Settings ***
Documentation     Testing that long variable value are truncated
Resource          atest_resource.robot

*** Test Cases ***
Without Max Assign Length
    Run Tests    ${EMPTY}    ./misc/long_variable_value.robot
    ${expected_value}=    Evaluate    '\${variable} = ' + 'a'*200
    ${XML}=    Parse output file
    Element Text Should Be    ${XML}    ${expected_value}    suite/test/kw[1]/msg    normalize_whitespace=yes

Max Assign Length 10
    [Template]    Positive Test
    10   10   ...

Max Assign Length 199
    [Template]    Positive Test
    199   199   ...

Max Assign Length Equals Value Length
    [Template]    Positive Test
    200   200

Max Assign Length More Than Value Length
    [Template]    Positive Test
    201   200

Invalid Values Max Assign Length
    Run Tests Without Processing Output    --maxassignlength 9    ./misc/long_variable_value.robot
    Stderr Should Be Equal To    [ ERROR ] Option '--maxassignlength' expected an integer value greater that 10 but got '9'.\n\nTry --help for usage information.\n


*** Keywords ***
Parse output file
    ${root} =    Parse XML    ${OUTFILE}
    RETURN    ${root}

Positive Test
    [Arguments]    ${maxassignlength}   ${exp_length}    ${dots}=${EMPTY}
    Run Tests    --maxassignlength ${maxassignlength}    ./misc/long_variable_value.robot
    ${expected_value}=    Evaluate    '\${variable} = ' + 'a'*${exp_length} + '${dots}'
    ${XML}=    Parse output file
    Element Text Should Be    ${XML}    ${expected_value}    suite/test/kw[1]/msg    normalize_whitespace=yes
