*** Settings ***
Library    Exceptions

*** Test Cases ***
150 X 14 Message Under The Limit
    Fail With Long Message    150    14

150 X 49 Message Under The Limit
    Fail With Long Message    150    49

2340 X 1 Message On The Limit
    Fail With Long Message    2340    1

7800 X 1 Message On The Limit
    Fail With Long Message    7800    1

8 X 31 Message Over The Limit
    Fail With Long Message    8    31

8 X 101 Message Over The Limit
    Fail With Long Message    8    101

400 X 7 Message Over The Limit
    Fail With Long Message    400    7

1500 X 7 Message Over The Limit
    Fail With Long Message    1500    7

*** Keywords ***
Fail With Long Message
    [Arguments]    ${line_length}=80    ${line_count}=1
    ${msg} =    Get Long Message    ${line_length}    ${line_count}
    Comment    Sanity check.    Must have triple quotes because    ${msg} contains newlines.
    Should Be True    len("""${msg}""") == ${line_length} * ${line_count}    Wrong length
    Fail    ${msg}

Get Long Message
    [Arguments]    ${line_length}=80    ${line_count}=1
    ${lines} =    Evaluate    [ str(i * ${line_length} + 1) for i in range(${line_count}) ]
    ${lines} =    Evaluate    [ line.ljust(${line_length} - 4) for line in ${lines} ]
    ${msg} =    Evaluate    "END\\n".join(${lines})
    ${total_chars} =    Evaluate    ${line_length} * ${line_count}
    ${msg} =    Evaluate    """${msg}"""[:-len("${total_chars}")] + " " * 4 + "${total_chars}"
    RETURN    ${msg}
