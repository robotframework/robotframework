*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for_in_range.robot
Resource          for_resource.robot

*** Test Cases ***
Only stop
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN RANGE loop     ${loop}    100
    Should be loop iteration    ${loop.kws[0]}                    \${i} = 0
    Check log message           ${loop.kws[0].kws[1].msgs[0]}     i: 0
    Should be loop iteration    ${loop.kws[1]}                    \${i} = 1
    Check log message           ${loop.kws[1].kws[1].msgs[0]}     i: 1
    Should be loop iteration    ${loop.kws[42]}                   \${i} = 42
    Check log message           ${loop.kws[42].kws[1].msgs[0]}    i: 42
    Should be loop iteration    ${loop.kws[-1]}                   \${i} = 99
    Check log message           ${loop.kws[-1].kws[1].msgs[0]}    i: 99

Start and stop
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN RANGE loop     ${loop}    4

Start, stop and step
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN RANGE loop     ${loop}    3
    Should be loop iteration    ${loop.kws[0]}    \${item} = 10
    Should be loop iteration    ${loop.kws[1]}    \${item} = 7
    Should be loop iteration    ${loop.kws[2]}    \${item} = 4

Float stop
    ${loop} =    Check test and get loop    ${TEST NAME} 1
    Should be IN RANGE loop     ${loop}    4
    Should be loop iteration    ${loop.kws[0]}    \${item} = 0.0
    Should be loop iteration    ${loop.kws[1]}    \${item} = 1.0
    Should be loop iteration    ${loop.kws[2]}    \${item} = 2.0
    Should be loop iteration    ${loop.kws[3]}    \${item} = 3.0
    ${loop} =    Check test and get loop    ${TEST NAME} 2
    Should be IN RANGE loop    ${loop}    3
    Should be loop iteration    ${loop.kws[0]}    \${item} = 0.0
    Should be loop iteration    ${loop.kws[1]}    \${item} = 1.0
    Should be loop iteration    ${loop.kws[2]}    \${item} = 2.0

Float start and stop
    ${loop} =    Check test and get loop    ${TEST NAME} 1
    Should be IN RANGE loop     ${loop}    3
    Should be loop iteration    ${loop.kws[0]}    \${item} = -1.5
    Should be loop iteration    ${loop.kws[1]}    \${item} = -0.5
    Should be loop iteration    ${loop.kws[2]}    \${item} = 0.5
    ${loop} =    Check test and get loop    ${TEST NAME} 2    0
    Should be IN RANGE loop     ${loop}    4
    Should be loop iteration    ${loop.kws[0]}    \${item} = -1.5
    Should be loop iteration    ${loop.kws[1]}    \${item} = -0.5
    Should be loop iteration    ${loop.kws[2]}    \${item} = 0.5
    Should be loop iteration    ${loop.kws[3]}    \${item} = 1.5

Float start, stop and step
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN RANGE loop     ${loop}    3
    Should be loop iteration    ${loop.kws[0]}    \${item} = 10.99
    Should be loop iteration    ${loop.kws[1]}    \${item} = 7.95
    Should be loop iteration    ${loop.kws[2]}    \${item} = 4.91

Variables in arguments
    ${loop} =    Check test and get loop    ${TEST NAME}    0
    Should be IN RANGE loop     ${loop}    2
    ${loop} =    Check test and get loop    ${TEST NAME}    2
    Should be IN RANGE loop     ${loop}    1

Calculations
    Check test case    ${TEST NAME}

Calculations with floats
    Check test case    ${TEST NAME}

Multiple variables
    ${loop} =    Check test and get loop    ${TEST NAME}    0
    Should be IN RANGE loop     ${loop}    1
    Should be loop iteration    ${loop.kws[0]}    \${a} = 0, \${b} = 1, \${c} = 2, \${d} = 3, \${e} = 4
    ${loop} =    Check test and get loop    ${TEST NAME}    2
    Should be IN RANGE loop     ${loop}    4
    Should be loop iteration    ${loop.kws[0]}    \${i} = -1, \${j} = 0, \${k} = 1
    Should be loop iteration    ${loop.kws[1]}    \${i} = 2, \${j} = 3, \${k} = 4
    Should be loop iteration    ${loop.kws[2]}    \${i} = 5, \${j} = 6, \${k} = 7
    Should be loop iteration    ${loop.kws[3]}    \${i} = 8, \${j} = 9, \${k} = 10

Too many arguments
    Check test and failed loop    ${TEST NAME}    IN RANGE

No arguments
    Check test and failed loop    ${TEST NAME}    IN RANGE

Non-number arguments
    Check test and failed loop    ${TEST NAME} 1   IN RANGE
    Check test and failed loop    ${TEST NAME} 2   IN RANGE

Wrong number of variables
    Check test and failed loop    ${TEST NAME}    IN RANGE

Non-existing variables in arguments
    Check test and failed loop    ${TEST NAME}    IN RANGE
