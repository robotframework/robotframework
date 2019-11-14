*** Settings ***
Suite Setup       Create input for Rebot
Suite Teardown    Remove Temp Files
Resource          rebot_resource.robot

*** Variables ***
${TEMP OUT 1}     %{TEMPDIR}${/}rebot-test-1.xml
${OUT PATTERN}    %{TEMPDIR}${/}rebot-test-?.*

*** Test Cases ***
Expand by 1 Name
    Run Rebot    --expandkeyword name:MyKeyword    ${TEMP OUT 1}
    fail  TODO: implement

Expand by 2 Names
    fail  TODO: implement

Expand by 3 Names
    fail  TODO: implement

Expand by 1 Tag
    fail  TODO: implement

Expand by 2 Tags
    fail  TODO: implement

Expand by 3 Tags
    fail  TODO: implement

Expand by Name and Tag
    fail  TODO: implement

No expand
    fail  TODO: implement

*** Keywords ***
Create input for Rebot
    Create Output With Robot    ${TEMP OUT 1}    --critical pass    misc/pass_and_fail.robot

Remove Temp Files
    Remove Files    ${OUT PATTERN}


