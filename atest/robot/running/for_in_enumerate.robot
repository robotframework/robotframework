*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for_in_enumerate.robot
Resource          for_resource.robot

*** Test Cases ***
Index and item
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}            4
    Should be FOR iteration        ${loop.body[0]}    \${index}=0    \${item}=a
    Should be FOR iteration        ${loop.body[1]}    \${index}=1    \${item}=b
    Should be FOR iteration        ${loop.body[2]}    \${index}=2    \${item}=c
    Should be FOR iteration        ${loop.body[3]}    \${index}=3    \${item}=d

Values from list variable
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}            4
    Should be FOR iteration        ${loop.body[0]}    \${index}=0    \${item}=a
    Should be FOR iteration        ${loop.body[1]}    \${index}=1    \${item}=b
    Should be FOR iteration        ${loop.body[2]}    \${index}=2    \${item}=c
    Should be FOR iteration        ${loop.body[3]}    \${index}=3    \${item}=d

Start
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}            5
    Should be FOR iteration        ${loop.body[0]}    \${index}=1    \${item}=1
    Should be FOR iteration        ${loop.body[1]}    \${index}=2    \${item}=2
    Should be FOR iteration        ${loop.body[2]}    \${index}=3    \${item}=3
    Should be FOR iteration        ${loop.body[3]}    \${index}=4    \${item}=4
    Should be FOR iteration        ${loop.body[4]}    \${index}=5    \${item}=5

Escape start
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}    2

Invalid start
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}    0    status=FAIL

Invalid variable in start
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}    0    status=FAIL

Index and two items
    ${loop} =    Check test and get loop    ${TEST NAME}    1
    Should be IN ENUMERATE loop    ${loop}           3
    Should be FOR iteration        ${loop.body[0]}    \${i}=0    \${item1}=a    \${item2}=b
    Should be FOR iteration        ${loop.body[1]}    \${i}=1    \${item1}=c    \${item2}=d
    Should be FOR iteration        ${loop.body[2]}    \${i}=2    \${item1}=e    \${item2}=f

Index and five items
    ${loop} =    Check test and get loop    ${TEST NAME}    1
    Should be IN ENUMERATE loop    ${loop}           2
    Should be FOR iteration        ${loop.body[0]}    \${x}=0    \${i1}=a    \${i2}=b    \${i3}=c    \${i4}=d    \${i5}=e
    Should be FOR iteration        ${loop.body[1]}    \${x}=1    \${i1}=f    \${i2}=g    \${i3}=h    \${i4}=i    \${i5}=j

One variable only
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}            3
    Should be FOR iteration        ${loop.body[0]}    \${item}=(0, 'a')
    Should be FOR iteration        ${loop.body[1]}    \${item}=(1, 'b')

Wrong number of variables
    Check test and failed loop    ${TEST NAME}    IN ENUMERATE

No values
    Check test and failed loop    ${TEST NAME}    IN ENUMERATE

No values with start
    Check test and failed loop    ${TEST NAME}    IN ENUMERATE
