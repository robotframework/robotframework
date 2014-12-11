*** Settings ***
Force Tags        regression    jybot    pybot
Resource          rebot_resource.robot

*** Test Cases ***
Output file content should be same with Robot and Rebot
    ${robot output} =    Generate output with Robot
    ${rebot output} =    Generate output with Rebot
    Elements should be equal    ${robot output}    ${rebot output}

*** Keywords ***
Generate output with Robot
    Run tests    -L TRACE -c fail    misc/pass_and_fail.robot
    Run keyword and return    Parse output file

Generate output with Rebot
    Run rebot    -c fail    ${OUTFILE}
    Run keyword and return    Parse output file

Parse output file
    ${root} =    Parse XML    ${OUTFILE}
    Remove element attributes    ${root}
    [Return]    ${root}
