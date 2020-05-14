*** Settings ***
Variables         variables_to_verify.py
Variables         length_variables.py

*** Variables ***
${scalar}         Hi tellus
${scalar 2}       Hello world

*** Test Cases ***
Variable Should Exist With Default Error Message
    [Documentation]    FAIL Variable '\${non-existing}' does not exist.
    Variable Should Exist    ${scalar}
    Variable Should Exist    ${non-existing}

Variable Should Exist With Given Error Message
    [Documentation]    FAIL My non-default error message
    Variable Should Exist    ${scalar}    This would be the error message
    Variable Should Exist    ${non-existing}    My non-default error message

Variable Should Exist With Error Message Containing Variables
    [Documentation]    FAIL Error with vars: ${scalar}
    Variable Should Exist    ${non-existing}    Error with vars: ${scalar}

Variable Should Exist Using $name format
    [Documentation]    FAIL Variable '\${non-existing}' does not exist.
    Variable Should Exist    $scalar    This would be the error message
    Variable Should Exist    $non-existing

Variable Should Exist Using Escaped format
    [Documentation]    FAIL Variable '\${non-existing}' does not exist.
    Variable Should Exist    \${scalar}
    Variable Should Exist    \${non-existing}

Variable Should Exist With Variables
    ${name} =    Set Variable    scalar
    Variable Should Exist    $${name}
    Variable Should Exist    $${name} ${2}

Variable Should Exist With Built In Variables
    Variable Should Exist    \${TEMPDIR}
    Variable Should Exist    \${/}
    Variable Should Exist    \${10}
    Variable Should Exist    \${TRUE}
    # Currently this is not working Variable Should Exist \${CURDIR}

Variable Should Exist With Extended Variable Syntax
    [Documentation]    FAIL Variable '\${length attribute.missing}' does not exist.
    Variable Should Exist    \${length attribute.length}
    Variable Should Exist    \${length attribute.missing}

Variable Should Exist With Extended Variable Syntax And Missing Object
    [Documentation]    FAIL Variable '\${missing.missing}' does not exist.
    Variable Should Exist    \${missing.missing}

Variable Should Exist With Invalid name 1
    [Documentation]    FAIL Invalid variable name 'invalid'.
    Variable Should Exist    invalid

Variable Should Exist With Invalid name 2
    [Documentation]    FAIL Invalid variable name '\\'.
    Variable Should Exist    \

Variable Should Not Exist With Default error message
    [Documentation]    FAIL Variable '\${scalar}' exists.
    Variable Should Not Exist    ${non-existing}
    Variable Should Not Exist    ${scalar}

Variable Should Not Exist With Given Error Message
    [Documentation]    FAIL This is the error message
    Variable Should Not Exist    ${non-existing}    This should not fail
    Variable Should Not Exist    ${scalar}    This is the error message

Variable Should Not Exist With Error Message Containing Variables
    [Documentation]    FAIL Error with vars: ${scalar} & ${42}
    Variable Should Not Exist    ${scalar}    Error with vars: ${scalar} & ${42}

Variable Should Not Exist With Built In Variables
    [Documentation]    FAIL Variable '\${10}' exists.
    Variable Should Not Exist    \${10}

Variable Should Not Exist With Extended Variable Syntax
    [Documentation]    FAIL Variable '\${length attribute.length}' exists.
    Variable Should Not Exist    \${length attribute.missing}
    Variable Should Not Exist    \${length attribute.length}

Variable Should Not Exist With Extended Variable Syntax And Missing Object
    Variable Should Not Exist    \${missing.missing}

Variable Should Not Exist Using $name format
    [Documentation]    FAIL Variable '\${scalar}' exists.
    Variable Should Not Exist    $non-existing
    Variable Should Not Exist    $scalar

Variable Should Not Exist Using Escaped format
    [Documentation]    FAIL Variable '\${scalar}' exists.
    Variable Should Not Exist    \${non-existing}
    Variable Should Not Exist    \${scalar}

Variable Should Not Exist With Variables
    ${name} =    Set Variable    nonex
    Variable Should Not Exist    $${name}
    Variable Should Not Exist    $${name}${name}${42}

Variable Should Not Exist With Invalid name 1
    [Documentation]    FAIL Invalid variable name 'invalid'.
    Variable Should Not Exist    invalid

Variable Should Not Exist With Invalid name 2
    [Documentation]    FAIL Invalid variable name '\\'.
    Variable Should Not Exist    \

Variable Should Exist In User Keyword When Variable Name Is Argument And Variable Exists
    Set Test Variable    ${foo}    \${bar}
    Check Variable Exists In UK    \${foo}

Variable Should Exist In User Keyword Fails When Variable Name Is Argument And Variable Does Not Exists
    [Documentation]    FAIL Variable '\${foo}' does not exist.
    Check Variable Exists In UK    \${foo}

Variable Should Not Exists In User Keyword When Variable Name Is Argument
    [Documentation]    FAIL Variable '\${foo}' exists.
    Check Variable Does Not Exist In UK    \${foo}
    Set Test Variable    ${foo}    \${bar}
    Check Variable Does Not Exist In UK    \${foo}

Variable Should Exist When Variable Has Variable Like Value
    ${variable} =    Set Variable    \${value}
    Variable Should Exist    \${variable}

Variable Should Not Exist Fails When Variable Has Variable Like Value
    [Documentation]    FAIL Variable '\${variable}' exists.
    ${variable} =    Set Variable    \${value}
    Variable Should Not Exist    \${variable}

*** Keywords ***
Check Variable Exists In UK
    [Arguments]    ${variable name}
    Variable Should Exist    ${variable name}

Check Variable Does Not Exist In UK
    [Arguments]    ${variable name}
    Variable Should Not Exist    ${variable name}
