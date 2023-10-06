*** Settings ***
Test Template     Output Encoding Should Work Correctly
Test Teardown     Safe Remove File    ${STDOUT}    ${STDERR}
Resource          process_resource.robot

*** Test Cases ***
Custom encoding when using default streams
    UTF-8
    Latin-1

Custom encoding when using custom streams
    UTF-8      stdout=${STDOUT}    stderr=${STDERR}
    Latin-1    stdout=${STDOUT}    stderr=${STDERR}

Console encoding
    SYSTEM
    SYSTEM     stdout=${STDOUT}    stderr=${STDERR}

System encoding
    SYSTEM
    SYSTEM     stdout=${STDOUT}    stderr=${STDERR}

Invalid encoding
    [Template]    Invalid Output Encoding Should Work Correctly
    Latin-1    ASCII
    Latin-1    ASCII    stdout=${STDOUT}    stderr=${STDERR}

*** Keywords ***
Output Encoding Should Work Correctly
    [Arguments]    ${encoding}    ${stdout}=${NONE}    ${stderr}=${NONE}
    ${result} =    Run Process With Output Encoding    ${encoding}
    ...    stdout=${stdout}    stderr=${stderr}
    Should Be Equal    ${result.stderr}    hyvä
    Should Be Equal    ${result.stdout}    hyvä

Invalid Output Encoding Should Work Correctly
    [Arguments]    ${encoding}    ${output_encoding}
    ...    ${stdout}=${NONE}    ${stderr}=${NONE}
    ${result} =    Run Process With Output Encoding    ${encoding}    ${output_encoding}
    ...    stdout=${stdout}    stderr=${stderr}
    ${expected} =    Set Variable If    sys.platform != 'cli'    hyv\\xe4    hyvä
    Should Be Equal    ${result.stderr}    ${expected}
    Should Be Equal    ${result.stdout}    ${expected}

Run Process With Output Encoding
    [Arguments]    ${encoding}    ${output_encoding}=${NONE}
    ...    ${stdout}=${NONE}    ${stderr}=${NONE}
    ${output_encoding} =    Evaluate    $output_encoding or $encoding
    ${result} =    Run Process    python    ${ENCODING SCRIPT}    encoding:${encoding}
    ...    stdout=${stdout}    stderr=${stderr}    output_encoding=${output encoding}
    RETURN    ${result}
