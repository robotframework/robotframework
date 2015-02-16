*** Variable ***
@{list}           Hello    world
${scalar}         Hi tellus

*** Test Case ***
Fail Unless Variable Exists 1
    [Documentation]    Default error message FAIL Variable \${non-existing} does not exist.
    Fail Unless Variable Exists    \${scalar}    This would be the error message
    Fail Unless Variable Exists    \${non-existing}

Fail Unless Variable Exists2
    [Documentation]    Non-default error message FAIL My non-default error message
    Fail Unless Variable Exists    \${non-existing}    My non-default error message

Fail Unless Variable Exists 3
    [Documentation]    Using the $name format FAIL Variable \${non-existing} does not exist.
    Fail Unless Variable Exists    $scalar    This would be the error message
    Fail Unless Variable Exists    $non-existing

Fail Unless Variable Exists 4
    [Documentation]    Invalid name FAIL Invalid variable syntax 'invalid'.
    Fail Unless Variable Exists    invalid

Fail Unless Variable Exists 5
    [Documentation]    Empty name FAIL Invalid variable syntax ''.
    Fail Unless Variable Exists    ${EMPTY}

Fail If Variable Exists 1
    [Documentation]    Default error message FAIL Variable \${scalar} exists.
    Fail If Variable Exists    \${non-existing}
    Variable Does Not Exist    \${scalar}

Fail If Variable Exists 2
    [Documentation]    Non-default error message FAIL This is the error message
    Variable Does Not Exist    \${scalar}    This is the error message

Fail If Variable Exists 3
    [Documentation]    Using the $name format FAIL Variable \${scalar} exists.
    Fail If Variable Exists    $non-existing
    Variable Does Not Exist    $scalar

Fail If Variable Exists 4
    [Documentation]    Invalid name FAIL Invalid variable syntax 'invalid'.
    Fail If Variable Exists    invalid

Fail If Variable Exists 5
    [Documentation]    Empty name FAIL Invalid variable syntax ''.
    Fail If Variable Exists    ${EMPTY}
