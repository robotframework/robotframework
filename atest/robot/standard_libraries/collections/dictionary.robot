*** Settings ***
Documentation     Tests for Collections library's dictionary functionality
Suite Setup       Run Tests    --loglevel debug    standard_libraries/collections/dictionary.robot
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

Shallow Copy Dictionary
    Check Test Case    ${TEST NAME}

Deep Copy Dictionary
    Check Test Case    ${TEST NAME}

Get Dictionary Keys Sorted
    Check Test Case    ${TEST NAME}

Get Dictionary Keys Unsorted
    Check Test Case    ${TEST NAME}

Get Dictionary Values Sorted
    Check Test Case    ${TEST NAME}

Get Dictionary Values Unsorted
    Check Test Case    ${TEST NAME}

Get Dictionary Items Sorted
    Check Test Case    ${TEST NAME}

Get Dictionary Items Unsorted
    Check Test Case    ${TEST NAME}

Get Dictionary Keys/Values/Items When Keys Are Unorderable
    Check Test Case    ${TEST NAME}

Get From Dictionary
    Check Test Case    ${TEST NAME}

Get From Dictionary With Invalid Key
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Get From Dictionary With Default
    Check Test Case    ${TEST NAME}

Log Dictionary With Different Log Levels
    ${tc} =    Check Test Case    ${TEST NAME}
    ${expected} =    Catenate    SEPARATOR=\n
    ...    Dictionary size is 3 and it contains following items:
    ...    a: 1
    ...    b: 2
    ...    c:
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

Pop From Dictionary Without Default
    Check Test Case    ${TEST NAME}

Pop From Dictionary With Default
    Check Test Case    ${TEST NAME}

Check invalid dictionary argument errors
    Check Test Case    ${TEST NAME}
