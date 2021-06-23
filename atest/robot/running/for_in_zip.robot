*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for_in_zip.robot
Resource          for_resource.robot

*** Test Cases ***
Two variables and lists
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=a    \${y}=x
    Should be FOR iteration    ${loop.body[1]}    \${x}=b    \${y}=y
    Should be FOR iteration    ${loop.body[2]}    \${x}=c    \${y}=z

Uneven lists
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=a    \${y}=1
    Should be FOR iteration    ${loop.body[1]}    \${x}=b    \${y}=2
    Should be FOR iteration    ${loop.body[2]}    \${x}=c    \${y}=3

Three variables and lists
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=a    \${y}=x    \${z}=1
    Should be FOR iteration    ${loop.body[1]}    \${x}=b    \${y}=y    \${z}=2
    Should be FOR iteration    ${loop.body[2]}    \${x}=c    \${y}=z    \${z}=3

Six variables and lists
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=a    \${y}=x    \${z}=1    \${å}=1    \${ä}=x    \${ö}=a
    Should be FOR iteration    ${loop.body[1]}    \${x}=b    \${y}=y    \${z}=2    \${å}=2    \${ä}=y    \${ö}=b
    Should be FOR iteration    ${loop.body[2]}    \${x}=c    \${y}=z    \${z}=3    \${å}=3    \${ä}=z    \${ö}=c

One variable and list
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=a
    Should be FOR iteration    ${loop.body[1]}    \${x}=b
    Should be FOR iteration    ${loop.body[2]}    \${x}=c

One variable and two lists
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=(${u}'a', ${u}'x')
    Should be FOR iteration    ${loop.body[1]}    \${x}=(${u}'b', ${u}'y')
    Should be FOR iteration    ${loop.body[2]}    \${x}=(${u}'c', ${u}'z')

One variable and six lists
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=(${u}'a', ${u}'x', ${u}'1', ${u}'1', ${u}'x', ${u}'a')
    Should be FOR iteration    ${loop.body[1]}    \${x}=(${u}'b', ${u}'y', ${u}'2', ${u}'2', ${u}'y', ${u}'b')
    Should be FOR iteration    ${loop.body[2]}    \${x}=(${u}'c', ${u}'z', ${u}'3', ${u}'3', ${u}'z', ${u}'c')

Other iterables
    Check Test Case    ${TEST NAME}

List variable containing iterables
    ${loop} =    Check test and get loop    ${TEST NAME}    2
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=a    \${y}=x    \${z}=f
    Should be FOR iteration    ${loop.body[1]}    \${x}=b    \${y}=y    \${z}=o
    Should be FOR iteration    ${loop.body[2]}    \${x}=c    \${y}=z    \${z}=o

List variable with iterables can be empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop    ${tc.body[0]}    0
    Should be IN ZIP loop    ${tc.body[1]}    0
    Check Log Message    ${tc.body[2].msgs[0]}    Executed!

Not iterable value
    Check test and failed loop    ${TEST NAME}    IN ZIP

Strings are not considered iterables
    Check test and failed loop    ${TEST NAME}    IN ZIP

Too few variables
    Check test and failed loop    ${TEST NAME} 1    IN ZIP    0
    Check test and failed loop    ${TEST NAME} 2    IN ZIP    1

Too many variables
    Check test and failed loop    ${TEST NAME} 1    IN ZIP    0
    Check test and failed loop    ${TEST NAME} 2    IN ZIP    1
