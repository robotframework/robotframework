*** Settings ***
Documentation     Verify that listeners see both the original test name and the resolved name.
...               Tests both using listener v2 and v3.
Suite Setup       Run With Listeners
Test Template     Original and resolved name should be available
Resource          listener_resource.robot

*** Test Cases ***
Test case name with variable
    \${NAME}    Name    \${VARIABLE}    Variable
    \${2}       2       \@{EMPTY}       []

Test case name with non-existing variable
    \${NAME}    Name    \${UNKNOWN VARIABLE}    \${UNKNOWN VARIABLE}

*** Keywords ***
Run With Listeners
    ${listeners} =    Catenate
    ...    --listener ${LISTENER DIR}/original_and_resolved_name_v2.py
    ...    --listener ${LISTENER DIR}/original_and_resolved_name_v3.py
    Run Tests    ${listeners}    output/listener_interface/variables_in_test_name.robot

Original and resolved name should be available
    [Arguments]    ${var1}    ${value1}    ${var2}    ${value2}
    ${resolved} =    Set Variable    Test Case "${value1}" With "${value2}"
    ${message} =    Catenate    SEPARATOR=\n
    ...    [START] [original] Test Case "${var1}" With "${var2}" [resolved] ${resolved}
    ...    [END] [original] Test Case "${var1}" With "${var2}" [resolved] ${resolved}
    # v3 listener sets test's message
    Check Test Case    ${resolved}    PASS    ${message}
    # v2 listener prints to stdout
    Stdout Should Contain    ${message}
