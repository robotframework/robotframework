*** Settings ***
Documentation     Tests for Collections library's list functionality
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/collections/list.robot
Force Tags        regression
Default Tags      jybot    pybot
Resource          atest_resource.robot

*** Test Cases ***
Convert To List
    Check Test Case    ${TEST NAME}

Convert To List With Invalid Type
    Check Test Case    ${TEST NAME}

Append To List
    Check Test Case    ${TEST NAME}

Insert Into List With String Index
    Check Test Case    ${TEST NAME}

Insert Into List With Int Index
    Check Test Case    ${TEST NAME}

Insert Into List With Index Over Lists Size
    Check Test Case    ${TEST NAME}

Insert Into List With Index Negative Index
    Check Test Case    ${TEST NAME}

Insert Into List With Index Under Lists Size
    Check Test Case    ${TEST NAME}

Insert Into List With Invalid Index
    Check Test Case    ${TEST NAME}

Combine Lists
    Check Test Case    ${TEST NAME}

Set List Value
    Check Test Case    ${TEST NAME}

Set List Value Index Out Of List
    Check Test Case    ${TEST NAME}

Set List Value With Invalid Index
    Check Test Case    ${TEST NAME}

Remove Values From List
    Check Test Case    ${TEST NAME}

Remove Non Existing Values From List
    Check Test Case    ${TEST NAME}

Remove From List
    Check Test Case    ${TEST NAME}

Remove From List Index Out Of List
    Check Test Case    ${TEST NAME}

Remove From List With Invalid Index
    Check Test Case    ${TEST NAME}

Remove Duplicates
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    0 duplicates removed.
    Check Log Message    ${tc.kws[2].msgs[0]}    3 duplicates removed.

Count Values In List
    Check Test Case    ${TEST NAME}

Count Values In List With Invalid Start Index
    Check Test Case    ${TEST NAME}

Count Values In List With Invalid Stop Index
    Check Test Case    ${TEST NAME}

Get Index From List
    Check Test Case    ${TEST NAME}

Get Index From List With Non Existing Value
    Check Test Case    ${TEST NAME}

Get Index From List With Invalid Start Index
    Check Test Case    ${TEST NAME}

Get Index From List With Invalid Stop Index
    Check Test Case    ${TEST NAME}

Copy List
    Check Test Case    ${TEST NAME}

Reserve List
    Check Test Case    ${TEST NAME}

Sort List
    Check Test Case    ${TEST NAME}

Get From List
    Check Test Case    ${TEST NAME}

Get From List With Invalid Index
    Check Test Case    ${TEST NAME}

Get From List Out Of List Index
    Check Test Case    ${TEST NAME}

Get Slice From List
    Check Test Case    ${TEST NAME}

Get Slice From List With Invalid Start Index
    Check Test Case    ${TEST NAME}

Get Slice From List With Invalid Stop Index
    Check Test Case    ${TEST NAME}

Get Slice From List With Out Of List Index
    Check Test Case    ${TEST NAME}

List Should Contain Value
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found and Own Error Message
    Check Test Case    ${TEST NAME}

List Should Not Contain Value
    Check Test Case    ${TEST NAME}

List Should Not Contain Value, Value Found
    Check Test Case    ${TEST NAME}

List Should Not Contain Value, Value Found and Own Error Message
    Check Test Case    ${TEST NAME}

List Should Not Contain Duplicates With No Duplicates
    Check Test Case    ${TEST NAME}

List Should Not Contain Duplicates Is Case And Space Sensitive
    Check Test Case    ${TEST NAME}

List Should Not Contain Duplicates With One Duplicate
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    'item' found 2 times.

List Should Not Contain Duplicates With Multiple Duplicates
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    '2' found 2 times.
    Check Log Message    ${tc.kws[1].msgs[1]}    'None' found 2 times.
    Check Log Message    ${tc.kws[1].msgs[2]}    '4' found 4 times.
    Check Log Message    ${tc.kws[1].msgs[3]}    '[1, 2, 3]' found 2 times.
    Check Log Message    ${tc.kws[1].msgs[4]}    '[]' found 10 times.

List Should Not Contain Duplicates With Custom Error Message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[2].msgs[0]}    '42' found 42 times.

Lists Should Be Equal
    Check Test Case    ${TEST NAME}

Lists Should Be equal With Different Lengths
    Check Test Case    ${TEST NAME}

Lists Should Be equal With Different Lengths And Own Error Message
    Check Test Case    ${TEST NAME}

Lists Should Be equal With Different Lengths And Own And Default Error Messages
    Check Test Case    ${TEST NAME}

Lists Should Be equal With Different Values
    Check Test Case    ${TEST NAME}

Lists Should Be equal With Different Values And Own Error Message
    Check Test Case    ${TEST NAME}

Lists Should Be equal With Different Values And Own And Default Error Messages
    Check Test Case    ${TEST NAME}

Lists Should Be Equal With Named Indices As List
    Check Test Case    ${TEST NAME}

Lists Should Be Equal With Named Indices As List With Too Few Values
    Check Test Case    ${TEST NAME}

Lists Should Be Equal With Named Indices As Dictionary
    Check Test Case    ${TEST NAME}

Lists Should Be Equal With Named Indices As Dictionary With Too Few Values
    Check Test Case    ${TEST NAME}

List Should Contain Sub List
    Check Test Case    ${TEST NAME}

List Should Contain Sub List With Missing Values
    Check Test Case    ${TEST NAME}

List Should Contain Sub List With Missing Values And Own Error Message
    Check Test Case    ${TEST NAME}

List Should Contain Sub List With Missing Values And Own and Default Error Messages
    Check Test Case    ${TEST NAME}

Log List With Different Log Levels
    ${tc} =    Check Test Case    ${TEST NAME}
    ${expected} =    Catenate    SEPARATOR=\n
    ...    List length is 3 and it contains following items:
    ...    0: 11
    ...    1: 12
    ...    2: 13
    Check Log Message    ${tc.kws[0].msgs[0]}    ${expected}    INFO
    Variable Should Not Exist    ${tc.kws[1].msgs[0]}
    Check Log Message    ${tc.kws[2].msgs[0]}    ${expected}    WARN
    Check Log Message    ${tc.kws[3].msgs[0]}    ${expected}    DEBUG
    Check Log Message    ${tc.kws[4].msgs[0]}    ${expected}    INFO

Log List With Different Lists
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    List is empty.    INFO
    Check Log Message    ${tc.kws[1].msgs[0]}    List has one item:\n1
    Check Log Message    ${tc.kws[4].msgs[0]}    List length is 2 and it contains following items:\n 0: (1, 2, 3)\n 1: 3.12

Count Matches In List Case Insensitive
    Check Test Case    ${TEST NAME}

Count Matches In List Whitespace Insensitive
    Check Test Case    ${TEST NAME}

Count Matches In List Regexp
    Check Test Case    ${TEST NAME}

Count Matches In List Glob
    Check Test Case    ${TEST NAME}

Get Matches In List Case Insensitive
    Check Test Case    ${TEST NAME}

Get Matches In List Whitespace Insensitive
    Check Test Case    ${TEST NAME}

Get Matches In List Regexp
    Check Test Case    ${TEST NAME}

Get Matches In List Glob
    Check Test Case    ${TEST NAME}

List Should Contain Value Case Insensitive
    Check Test Case    ${TEST NAME}

List Should Contain Value Whitespace Insensitive
    Check Test Case    ${TEST NAME}

List Should Contain Value Regexp
    Check Test Case    ${TEST NAME}

List Should Contain Value Glob
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found Case Insensitive
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found Whitespace Insensitive
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found Regexp
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found Glob
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found And Own Error Message Case Insensitive
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found And Own Error Message Whitespace Insensitive
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found and Own Error Message Regexp
    Check Test Case    ${TEST NAME}

List Should Contain Value, Value Not Found and Own Error Message Glob
    Check Test Case    ${TEST NAME}

List Should Not Contain Value Case Insensitive
    Check Test Case    ${TEST NAME}

List Should Not Contain Value Whitespace Insensitive
    Check Test Case    ${TEST NAME}

List Should Not Contain Value Regexp
    Check Test Case    ${TEST NAME}

List Should Not Contain Value Glob
    Check Test Case    ${TEST NAME}

List Should Not Contain Value, Value Found Case Insensitive
    Check Test Case    ${TEST NAME}

List Should Not Contain Value, Value Found Whitespace Insensitive
    Check Test Case    ${TEST NAME}

List Should Not Contain Value, Value Found Regexp
    Check Test Case    ${TEST NAME}

List Should Not Contain Value, Value Found Glob
    Check Test Case    ${TEST NAME}

List Should Not Contain Value, Value Found and Own Error Message Case Insensitive
    Check Test Case    ${TEST NAME}

List Should Not Contain Value, Value Found and Own Error Message Regexp
    Check Test Case    ${TEST NAME}

List Should Not Contain Value, Value Found and Own Error Message Glob
    Check Test Case    ${TEST NAME}
