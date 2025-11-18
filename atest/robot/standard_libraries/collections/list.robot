*** Settings ***
Documentation     Tests for Collections library's list functionality
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/collections/list.robot
Resource          atest_resource.robot

*** Test Cases ***
Convert To List
    Check Test Case    ${TEST NAME}

Convert To List With Invalid Type
    Check Test Case    ${TEST NAME}

Append To List
    Check Test Case    ${TEST NAME}

Insert Into List
    Check Test Case    ${TEST NAME}

Insert Into List with invalid index
    Check Test Case    ${TEST NAME}

Combine Lists
    Check Test Case    ${TEST NAME}

Set List Value
    Check Test Case    ${TEST NAME}

Set List Value with invalid index
    Check Test Case    ${TEST NAME}

Remove Values From List
    Check Test Case    ${TEST NAME}

Remove From List
    Check Test Case    ${TEST NAME}

Remove From List with invalid index
    Check Test Case    ${TEST NAME}

Remove Duplicates
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0, 0, 0]}    0 duplicates removed.
    Check Log Message    ${tc[1, 0, 0, 0]}    3 duplicates removed.

Count Values In List
    Check Test Case    ${TEST NAME}

Count Values In List with invalid index
    Check Test Case    ${TEST NAME}

Get Index From List
    Check Test Case    ${TEST NAME}

Get Index From List with empty string as start index is deprecated
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0, 0, 0]}
    ...    Using an empty string as a start index with the 'Get Index From List' keyword is deprecated. Use '0' instead.
    ...    WARN

Get Index From List with invalid index
    Check Test Case    ${TEST NAME}

Copy List
    Check Test Case    ${TEST NAME}

Shallow Copy List
    Check Test Case    ${TEST NAME}

Deep Copy List
    Check Test Case    ${TEST NAME}

Reverse List
    Check Test Case    ${TEST NAME}

Sort List
    Check Test Case    ${TEST NAME}

Sorting Unsortable List Fails
    Check Test Case    ${TEST NAME}

Get From List
    Check Test Case    ${TEST NAME}

Get From List with invalid index
    Check Test Case    ${TEST NAME}

Get Slice From List
    Check Test Case    ${TEST NAME}

Get Slice From List with empty string as start index is deprecated
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0, 0, 0]}
    ...    Using an empty string as a start index with the 'Get Slice From List' keyword is deprecated. Use '0' instead.
    ...    WARN

Get Slice From List with invalid index
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
    Check Log Message    ${tc[1, 0]}    'item' found 2 times.

List Should Not Contain Duplicates With Multiple Duplicates
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 0]}    '2' found 2 times.
    Check Log Message    ${tc[1, 1]}    'None' found 2 times.
    Check Log Message    ${tc[1, 2]}    '4' found 4 times.
    Check Log Message    ${tc[1, 3]}    '[1, 2, 3]' found 2 times.
    Check Log Message    ${tc[1, 4]}    '[]' found 10 times.

List Should Not Contain Duplicates With Custom Error Message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 0]}    '6' found 7 times.

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

Lists Should Be Equal Ignore Order
    Check Test Case    ${TEST NAME}

Ignore Order Is Recursive
    Check Test Case    ${TEST NAME}

List Should Contain Sub List
    Check Test Case    ${TEST NAME}

List Should Contain Sub List With Missing Values
    Check Test Case    ${TEST NAME}

List Should Contain Sub List When The Only Missing Value Is Empty String
    Check Test Case    ${TEST NAME}

List Should Contain Sub List With Missing Values And Own Error Message
    Check Test Case    ${TEST NAME}

List Should Contain Sub List With Missing Values And Own and Default Error Messages
    Check Test Case    ${TEST NAME}

'NO VALUES' is deprecated
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}   Using 'NO VALUES' for disabling the 'values' argument is deprecated. Use 'values=False' instead.    WARN
    Check Log Message    ${tc[1, 0]}   Using 'no values' for disabling the 'values' argument is deprecated. Use 'values=False' instead.    WARN

Log List
    ${tc} =    Check Test Case    ${TEST NAME}
    VAR    ${three items}
    ...    List length is 3 and it contains following items:
    ...    0: 11
    ...    1: 12
    ...    2: 13
    ...    separator=\n
    Check Log Message    ${tc[0, 0]}    List is empty.    INFO
    Check Log Message    ${tc[1, 0]}    ${three items}    INFO
    Check Log Message    ${tc[2, 0]}    ${three items}    INFO
    Should Be Empty      ${tc[3].body}
    Check Log Message    ${tc[4, 0]}    ${three items}    WARN
    Check Log Message    ${tc[5, 0]}    ${three items}    DEBUG

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

Lists Should Be Equal With Ignore Case
    Check Test Case    ${TEST NAME}

List Should Contain Value With Ignore Case
    Check Test Case    ${TEST NAME}

List Should Not Contain Value With Ignore Case Does Contain Value
    Check Test Case    ${TEST NAME}

List Should Contain Sub List With Ignore Case
    Check Test Case    ${TEST NAME}

List Should Not Contain Duplicates With Ignore Case
    Check Test Case    ${TEST NAME}

List Should Contain Value With Ignore Case And Nested List and Dictionary
    Check Test Case    ${TEST NAME}

Lists Should be equal with Ignore Case and Order
    Check Test Case    ${TEST NAME}

Validate argument conversion errors
    Check Test Case    ${TEST NAME}
