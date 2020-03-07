*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for_dict_iteration.robot
Resource          for_resource.robot

*** Test Cases ***
FOR loop with one variable
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be FOR loop          ${loop}           3
    Should be loop iteration    ${loop.kws[0]}    \${item} = (${u}'a', ${u}'1')
    Should be loop iteration    ${loop.kws[1]}    \${item} = (${u}'b', ${u}'2')
    Should be loop iteration    ${loop.kws[2]}    \${item} = (${u}'c', ${u}'3')

FOR loop with two variables
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be FOR loop          ${loop}           3
    Should be loop iteration    ${loop.kws[0]}    \${key} = a, \${value} = 1
    Should be loop iteration    ${loop.kws[1]}    \${key} = b, \${value} = 2
    Should be loop iteration    ${loop.kws[2]}    \${key} = c, \${value} = 3

FOR loop with more than two variables is invalid
    Check test and failed loop    ${TESTNAME}

FOR IN ENUMERATE loop with one variable
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be IN ENUMERATE loop    ${loop}           3
    Should be loop iteration       ${loop.kws[0]}    \${var} = (0, ${u}'a', ${u}'1')
    Should be loop iteration       ${loop.kws[1]}    \${var} = (1, ${u}'b', ${u}'2')
    Should be loop iteration       ${loop.kws[2]}    \${var} = (2, ${u}'c', ${u}'3')

FOR IN ENUMERATE loop with two variables
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be IN ENUMERATE loop    ${loop}           3
    Should be loop iteration       ${loop.kws[0]}    \${index} = 0, \${item} = (${u}'a', ${u}'1')
    Should be loop iteration       ${loop.kws[1]}    \${index} = 1, \${item} = (${u}'b', ${u}'2')
    Should be loop iteration       ${loop.kws[2]}    \${index} = 2, \${item} = (${u}'c', ${u}'3')

FOR IN ENUMERATE loop with three variables
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be IN ENUMERATE loop    ${loop}           3
    Should be loop iteration       ${loop.kws[0]}    \${i} = 0, \${k} = a, \${v} = 1
    Should be loop iteration       ${loop.kws[1]}    \${i} = 1, \${k} = b, \${v} = 2
    Should be loop iteration       ${loop.kws[2]}    \${i} = 2, \${k} = c, \${v} = 3

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

Only 'key=value' syntax
    Check Test Case    ${TESTNAME}

Last value wins
    Check Test Case    ${TESTNAME}

'key=value' syntax with variables
    Check Test Case    ${TESTNAME}

Equal sign in variable
    Check Test Case    ${TESTNAME}

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

Equal sign in variable doesn't initiate dict iteration
    ${loop} =    Check test and get loop    ${TESTNAME}
    Should be FOR loop          ${loop}           2
    Should be loop iteration    ${loop.kws[0]}    \${item} = =
    Should be loop iteration    ${loop.kws[1]}    \${item} = =

'key=value' syntax with normal values doesn't initiate dict iteration
    ${loop} =    Check test and get loop    ${TESTNAME} 1
    Should be FOR loop          ${loop}           3
    Should be loop iteration    ${loop.kws[0]}    \${item} = a=1
    Should be loop iteration    ${loop.kws[1]}    \${item} = normal
    Should be loop iteration    ${loop.kws[2]}    \${item} = c=3
    ${loop} =    Check test and get loop    ${TESTNAME} 2
    Should be FOR loop          ${loop}           3
    Should be loop iteration    ${loop.kws[0]}    \${item} = a=1
    Should be loop iteration    ${loop.kws[1]}    \${item} = b=2
    Should be loop iteration    ${loop.kws[2]}    \${item} = c=3
