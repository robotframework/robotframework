*** Settings ***
Library           Exceptions

*** Test Cases ***
50 X 1 Message Under The Limit
    Fail With Long Message    50    1

100 X 1 Message Under The Limit
    Fail With Long Message    100    1

50 X 10 Message Under The Limit
    Fail With Long Message    50    10

150 X 19 Message Under The Limit
    Fail With Long Message    150    9

77 X 39 Message Under The Limit
    Fail With Long Message    77    39

20 X 40 Message On The Limit
    Fail With Long Message    20    40

150 X 20 Message On The Limit
    Fail With Long Message    150    20

3120 X 1 Message On The Limit
    Fail With Long Message    3120    1

8 X 41 Message Over The Limit
    Fail With Long Message    8    41

400 X 7 Message Over The Limit
    Fail With Long Message    400    7

3121 X 1 Message Over The Limit
    Fail With Long Message    3121    1

Multiple short errors
    FOR    ${index}    IN RANGE    1    100
        Raise Continuable Failure    Failure number ${index}
    END

Two long errors
    ${err}=    Get Long Message    40    50
    Raise Continuable Failure    ${err}
    Raise Continuable Failure    ${err.replace(' ', '~')}

*** Keywords ***
Fail With Long Message
    [Arguments]    ${line_length}=80    ${line_count}=1
    ${msg} =    Get Long Message    ${line_length}    ${line_count}
    # Sanity check
    Should Be True    len($msg) == ${line_length} * ${line_count}    Wrong length
    Fail    ${msg}

Get Long Message
    [Arguments]    ${line_length}=80    ${line_count}=1
    ${lines} =    Evaluate    [str(i * ${line_length} + 1) for i in range(${line_count})]
    ${lines} =    Evaluate    [line.ljust(${line_length} - 4) for line in $lines]
    ${msg} =    Evaluate    "END\\n".join($lines)
    ${total_chars} =    Evaluate    ${line_length} * ${line_count}
    ${msg} =    Evaluate    $msg[:-len("${total_chars}")] + " " * 4 + "${total_chars}"
    RETURN    ${msg}
