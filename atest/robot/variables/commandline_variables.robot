*** Setting ***
Documentation     How variables from CLI override other variables is tested in variable_priorities.robot
Suite Setup       Run Test Data
Resource          atest_resource.robot

*** Test Case ***
Normal Text
    Check Test Case    Normal Text

Escaped Text
    Check Test Case    Escaped Text

No Colon In Variable
    Check Test Case    No Colon In Variable

*** Keyword ***
Run Test Data
    ${escaped} =    Set Variable    QUOTIAPOSll take spam AMP eggsEXCLAMEXCLAMQUOT    # "I'll take spam & eggs!!"
    ${escaped2} =    Set Variable    DOLLARCURLY1notvarCURLY2    # \${notvar}
    ${options} =    Catenate
    ...    --variable NORMAL_TEXT:Hello
    ...    --variable no_colon
    ...    -v ESCAPED:${escaped .replace(' ', 'SPACE')}
    ...    --variable eScApEd2:${escaped2}
    ...    -E quot:QUOT    -E apos:APOS    -E dollar:DOLLAR    -E amp:AMP
    ...    -E space:SPACE    -E exclam:EXCLAM    -E curly1:CURLY1    -E curly2:CURLY2
    Run Tests    ${options}    variables/commandline_variables.robot
