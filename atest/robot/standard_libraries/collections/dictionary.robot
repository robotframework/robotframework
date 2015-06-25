*** Settings ***
Documentation     Tests for Collections library's dictionary functionality
Suite Setup       Run Tests    --loglevel debug    standard_libraries/collections/dictionary.robot
Force Tags        regression
Default Tags      jybot    pybot
Resource          atest_resource.robot

*** Test Cases ***
Convert To Dictionary
    Check Test Case    ${TEST NAME}

Set To Dictionary
    Check Test Case    ${TEST NAME}

Set To Dictionary With wrong number of arguments
    Check Test Case    ${TEST NAME}

Set To Dictionary With **kwargs
    Check Test Case    ${TEST NAME}

Remove From Dictionary
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Removed item with key 'b' and value '2'.
    Check Log Message    ${tc.kws[0].msgs[1]}    Key 'x' not found.
    Check Log Message    ${tc.kws[0].msgs[2]}    Key '2' not found.

Keep In Dictionary
    Check Test Case    ${TEST NAME}

Copy Dictionary
    Check Test Case    ${TEST NAME}

Get Dictionary Keys
    Check Test Case    ${TEST NAME}

Get Dictionary Values
    Check Test Case    ${TEST NAME}

Get Dictionary Items
    Check Test Case    ${TEST NAME}

Get From Dictionary
    Check Test Case    ${TEST NAME}

Get From Dictionary With Invalid Key
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Key
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Key With Missing Key
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Item
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Item With Missing Key
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Item With Wrong Value
    Check Test Case    ${TEST NAME}

Dictionary Should Not Contain Key
    Check Test Case    ${TEST NAME}

Dictionary Should Not Contain Key With Existing Key
    Check Test Case    ${TEST NAME}

Dictionary Should (Not) Contain Key Does Not Require `has_key`
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Value
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Value With Missing Value
    Check Test Case    ${TEST NAME}

Dictionary Should Not Contain Value
    Check Test Case    ${TEST NAME}

Dictionary Should Not Contain Value With Existing Value
    Check Test Case    ${TEST NAME}

Dictionaries Should Be Equal
    Check Test Case    ${TEST NAME}

Dictionaries Should Equal With First Dictionary Missing Keys
    Check Test Case    ${TEST NAME}

Dictionaries Should Equal With Second Dictionary Missing Keys
    Check Test Case    ${TEST NAME}

Dictionaries Should Equal With Both Dictionaries Missing Keys
    Check Test Case    ${TEST NAME}

Dictionaries Should Be Equal With Different Keys And Own Error Message
    Check Test Case    ${TEST NAME}

Dictionaries Should Be Equal With Different Keys And Own And Default Error Messages
    Check Test Case    ${TEST NAME}

Dictionaries Should Be Equal With Different Values
    Check Test Case    ${TEST NAME}

Dictionaries Should Be Equal With Different Values And Own Error Message
    Check Test Case    ${TEST NAME}

Dictionaries Should Be Equal With Different Values And Own And Default Error Messages
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Sub Dictionary
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Sub Dictionary With Missing Keys
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Sub Dictionary With Missing Keys And Own Error Message
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Sub Dictionary With Missing Keys And Own And Default Error Message
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Sub Dictionary With Different Value
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Sub Dictionary With Different Value And Own Error Message
    Check Test Case    ${TEST NAME}

Dictionary Should Contain Sub Dictionary With Different Value And Own And Default Error Message
    Check Test Case    ${TEST NAME}

Log Dictionary With Different Log Levels
    ${tc} =    Check Test Case    ${TEST NAME}
    ${expected} =    Catenate    SEPARATOR=\n
    ...    Dictionary size is 3 and it contains following items:
    ...    3: None
    ...    a: 1
    ...    b: 2
    Check Log Message    ${tc.kws[0].msgs[0]}    ${expected}    INFO
    Should Be Empty    ${tc.kws[1].msgs}
    Check Log Message    ${tc.kws[2].msgs[0]}    ${expected}    WARN
    Check Log Message    ${tc.kws[3].msgs[0]}    ${expected}    DEBUG
    Check Log Message    ${tc.kws[4].msgs[0]}    ${expected}    INFO

Log Dictionary With Different Dictionaries
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Dictionary is empty.
    Check Log Message    ${tc.kws[1].msgs[0]}    Dictionary has one item:\na: 1
    Check Log Message    ${tc.kws[3].msgs[0]}    Dictionary size is 3 and it contains following items:\nTrue: xxx\nfoo: []\n(1, 2, 3): 3.14
