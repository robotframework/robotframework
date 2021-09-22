*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for_dict_iteration.robot
Resource          for_resource.robot

*** Test Cases ***
FOR loop with one variable
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be FOR loop         ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${item}=('a', '1')
    Should be FOR iteration    ${loop.body[1]}    \${item}=('b', '2')
    Should be FOR iteration    ${loop.body[2]}    \${item}=('c', '3')

FOR loop with two variables
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be FOR loop         ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${key}=a    \${value}=1
    Should be FOR iteration    ${loop.body[1]}    \${key}=b    \${value}=2
    Should be FOR iteration    ${loop.body[2]}    \${key}=c    \${value}=3

FOR loop with more than two variables is invalid
    Check test and failed loop    ${TESTNAME}

FOR IN ENUMERATE loop with one variable
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be IN ENUMERATE loop    ${loop}            3
    Should be FOR iteration        ${loop.body[0]}    \${var}=(0, 'a', '1')
    Should be FOR iteration        ${loop.body[1]}    \${var}=(1, 'b', '2')
    Should be FOR iteration        ${loop.body[2]}    \${var}=(2, 'c', '3')

FOR IN ENUMERATE loop with two variables
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be IN ENUMERATE loop    ${loop}            3
    Should be FOR iteration        ${loop.body[0]}    \${index}=0    \${item}=('a', '1')
    Should be FOR iteration        ${loop.body[1]}    \${index}=1    \${item}=('b', '2')
    Should be FOR iteration        ${loop.body[2]}    \${index}=2    \${item}=('c', '3')

FOR IN ENUMERATE loop with three variables
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be IN ENUMERATE loop    ${loop}            3
    Should be FOR iteration        ${loop.body[0]}    \${i}=0    \${k}=a    \${v}=1
    Should be FOR iteration        ${loop.body[1]}    \${i}=1    \${k}=b    \${v}=2
    Should be FOR iteration        ${loop.body[2]}    \${i}=2    \${k}=c    \${v}=3

FOR IN ENUMERATE loop with start
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be IN ENUMERATE loop    ${loop}           3

FOR IN ENUMERATE loop with more than three variables is invalid
    Check test and failed loop    ${TESTNAME}    IN ENUMERATE

FOR IN RANGE loop doesn't support dict iteration
    Check test and failed loop    ${TESTNAME}    IN RANGE

FOR IN ZIP loop doesn't support dict iteration
    Check test and failed loop    ${TESTNAME}    IN ZIP

Multiple dict variables
    Check Test Case    ${TESTNAME}

Dict variable with 'key=value' syntax
    Check Test Case    ${TESTNAME}

Last value wins
    Check Test Case    ${TESTNAME}

Equal sign in variable
    Check Test Case    ${TESTNAME}

'key=value' alone is still considered "normal" iteration
    ${tc} =    Check Test Case    ${TESTNAME}
    ${message} =    Catenate
    ...    FOR loop iteration over values that are all in 'name=value' format like 'a=1' is deprecated.
    ...    In the future this syntax will mean iterating over names and values separately like when iterating over '\&{dict} variables.
    ...    Escape at least one of the values like 'a\\=1' to use normal FOR loop iteration and to disable this warning.
    Check Log Message    ${tc.body[0].msgs[0]}    ${message}    WARN
    Check Log Message    ${ERRORS}[0]             ${message}    WARN
    ${message} =    Catenate
    ...    FOR loop iteration over values that are all in 'name=value' format like 'x==1' is deprecated.
    ...    In the future this syntax will mean iterating over names and values separately like when iterating over '\&{dict} variables.
    ...    Escape at least one of the values like 'x\\==1' to use normal FOR loop iteration and to disable this warning.
    Check Log Message    ${tc.body[2].msgs[0]}    ${message}    WARN
    Check Log Message    ${ERRORS}[1]             ${message}    WARN

Non-string keys
    Check Test Case    ${TESTNAME}

Invalid key
    Check Test Case    ${TESTNAME}

Invalid dict
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Non-existing variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Dict variables and invalid values
    Check test and failed loop    ${TESTNAME} 1
    Check test and failed loop    ${TESTNAME} 2
    Check test and failed loop    ${TESTNAME} 3

Equal sign in variable doesn't initiate dict iteration
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be FOR loop         ${loop}           2
    Should be FOR iteration    ${loop.body[0]}    \${item}==
    Should be FOR iteration    ${loop.body[1]}    \${item}==

'key=value' syntax with normal values doesn't initiate dict iteration
    ${loop} =    Check test and get loop    ${TESTNAME} 1
    Should be FOR loop         ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${item}=a=1
    Should be FOR iteration    ${loop.body[1]}    \${item}=normal
    Should be FOR iteration    ${loop.body[2]}    \${item}=c=3
    ${loop} =    Check test and get loop    ${TESTNAME} 2
    Should be FOR loop         ${loop}            3
    Should be FOR iteration    ${loop.body[0]}    \${item}=a=1
    Should be FOR iteration    ${loop.body[1]}    \${item}=b=2
    Should be FOR iteration    ${loop.body[2]}    \${item}=c=3
