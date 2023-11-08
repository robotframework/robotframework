*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for/for_in_zip.robot
Resource          for.resource

*** Test Cases ***
Two variables and lists
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=a    \${y}=x
    Should be FOR iteration    ${loop.body[1]}    \${x}=b    \${y}=y
    Should be FOR iteration    ${loop.body[2]}    \${x}=c    \${y}=z

Uneven lists cause deprecation warning by default
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Check Log Message          ${loop.body[0]}
    ...    FOR IN ZIP default mode will be changed from SHORTEST to STRICT in Robot Framework 8.0. Use 'mode=SHORTEST' to keep using the SHORTEST mode. If the mode is not changed, execution will fail like this in the future: FOR IN ZIP items must have equal lengths in the STRICT mode, but lengths are 3 and 5.    WARN
    Should be FOR iteration    ${loop.body[1]}    \${x}=a    \${y}=1
    Should be FOR iteration    ${loop.body[2]}    \${x}=b    \${y}=2
    Should be FOR iteration    ${loop.body[3]}    \${x}=c    \${y}=3

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
    Should be FOR iteration    ${loop.body[0]}    \${x}=('a', 'x')
    Should be FOR iteration    ${loop.body[1]}    \${x}=('b', 'y')
    Should be FOR iteration    ${loop.body[2]}    \${x}=('c', 'z')

One variable and six lists
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=('a', 'x', 1, 1, 'x', 'a')
    Should be FOR iteration    ${loop.body[1]}    \${x}=('b', 'y', 2, 2, 'y', 'b')
    Should be FOR iteration    ${loop.body[2]}    \${x}=('c', 'z', 3, 3, 'z', 'c')

Other iterables
    Check Test Case    ${TEST NAME}

List variable containing iterables
    ${loop} =    Check test and get loop    ${TEST NAME}    1
    Should be IN ZIP loop      ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${x}=a    \${y}=x    \${z}=f
    Should be FOR iteration    ${loop.body[1]}    \${x}=b    \${y}=y    \${z}=o
    Should be FOR iteration    ${loop.body[2]}    \${x}=c    \${y}=z    \${z}=o

List variable with iterables can be empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}            1         NOT RUN
    Should be FOR iteration    ${tc.body[0].body[0]}    \${x}=
    Should be IN ZIP loop      ${tc.body[1]}            1         NOT RUN
    Should be FOR iteration    ${tc.body[1].body[0]}    \${x}=    \${y}=    \${z}=
    Check Log Message          ${tc.body[2].msgs[0]}    Executed!

Strict mode
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    3   PASS    mode=STRICT
    Should be IN ZIP loop      ${tc.body[2]}    1   FAIL    mode=strict

Strict mode requires items to have length
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    1   FAIL    mode=STRICT

Shortest mode
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    3   PASS    mode=SHORTEST    fill=ignored
    Should be IN ZIP loop      ${tc.body[3]}    3   PASS    mode=\${{'shortest'}}

Shortest mode supports infinite iterators
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    3   PASS    mode=SHORTEST

Longest mode
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    3   PASS    mode=LONGEST
    Should be IN ZIP loop      ${tc.body[3]}    5   PASS    mode=LoNgEsT

Longest mode with custom fill value
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    5   PASS    mode=longest    fill=?
    Should be IN ZIP loop      ${tc.body[3]}    3   PASS    mode=longest    fill=\${0}

Invalid mode
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    1   FAIL    mode=bad

Invalid mode from variable
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    1   FAIL    mode=\${{'bad'}}

Config more than once
    ${tc} =    Check Test Case    ${TEST NAME} 1
    Should be IN ZIP loop      ${tc.body[0]}    1   FAIL    mode=shortest
    ${tc} =    Check Test Case    ${TEST NAME} 2
    Should be IN ZIP loop      ${tc.body[0]}    1   FAIL    fill=z

Non-existing variable in mode
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    1   FAIL    mode=\${bad}    fill=\${ignored}

Non-existing variable in fill value
    ${tc} =    Check Test Case    ${TEST NAME}
    Should be IN ZIP loop      ${tc.body[0]}    1   FAIL    mode=longest    fill=\${bad}

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
