*** Settings ***
Suite Setup       Create input for Rebot
Suite Teardown    Remove Temp Files
Resource          rebot_resource.robot

*** Variables ***
${TEMP OUT 1}     %{TEMPDIR}${/}rebot-test-1.xml
${OUT PATTERN}    %{TEMPDIR}${/}rebot-test-?.*

*** Test Cases ***
Expand by 1 Name via rebot
    Run Rebot    --expandkeyword name:MyKeyword    ${TEMP OUT 1}
    fail  TODO: implement

Expand by 3 Names via rebot
    fail  TODO: implement

Expand by 1 Tag via rebot
    fail  TODO: implement

Expand by 3 Tags via rebot
    fail  TODO: implement

Expand by Name and Tag via rebot
    fail  TODO: implement

No expand via rebot
    fail  TODO: implement

Expand by 1 Name via robot
    Run Robot    --expandkeyword name:MyKeyword    ${TEMP OUT 1}
    fail  TODO: implement

Expand by 3 Names via robot
    fail  TODO: implement

Expand by 1 Tag via robot
    fail  TODO: implement

Expand by 3 Tags via robot
    fail  TODO: implement

Expand by Name and Tag via robot
    fail  TODO: implement

No expand via robot
    fail  TODO: implement

*** Keywords ***
Create input for Rebot
    Create Output With Robot    ${TEMP OUT 1}    --critical pass    misc/pass_and_fail.robot

Remove Temp Files
    Remove Files    ${OUT PATTERN}


