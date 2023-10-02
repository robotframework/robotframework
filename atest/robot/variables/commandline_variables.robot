*** Settings ***
Documentation     How variables from CLI override other variables is tested in variable_priorities.robot
Suite Setup       Run Tests With Variables
Resource          atest_resource.robot

*** Test Cases ***
Normal Text
    Check Test Case    ${TEST NAME}

Special Characters
    Check Test Case    ${TEST NAME}

No Colon In Variable
    Check Test Case    ${TEST NAME}

*** Keywords ***
Run Tests With Variables
    ${options} =    Catenate
    ...    --variable NORMAL_TEXT:Hello
    ...    --variable no_colon
    ...    -v "SPECIAL:I'll take spam & eggs!!"
    ...    --variable sPEciAL2:\${notvar}
    Run Tests    ${options}    variables/commandline_variables.robot
