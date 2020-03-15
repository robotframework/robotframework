*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for_in_enumerate.robot
Resource          for_resource.robot

*** Test Cases ***
Index and item
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}           4
    Should be loop iteration       ${loop.kws[0]}    \${index} = 0, \${item} = a
    Should be loop iteration       ${loop.kws[1]}    \${index} = 1, \${item} = b
    Should be loop iteration       ${loop.kws[2]}    \${index} = 2, \${item} = c
    Should be loop iteration       ${loop.kws[3]}    \${index} = 3, \${item} = d

Values from list variable
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}           4
    Should be loop iteration       ${loop.kws[0]}    \${index} = 0, \${item} = a
    Should be loop iteration       ${loop.kws[1]}    \${index} = 1, \${item} = b
    Should be loop iteration       ${loop.kws[2]}    \${index} = 2, \${item} = c
    Should be loop iteration       ${loop.kws[3]}    \${index} = 3, \${item} = d

Index and two items
    ${loop} =    Check test and get loop    ${TEST NAME}    1
    Should be IN ENUMERATE loop    ${loop}           3
    Should be loop iteration       ${loop.kws[0]}    \${i} = 0, \${item1} = a, \${item2} = b
    Should be loop iteration       ${loop.kws[1]}    \${i} = 1, \${item1} = c, \${item2} = d
    Should be loop iteration       ${loop.kws[2]}    \${i} = 2, \${item1} = e, \${item2} = f

Index and five items
    ${loop} =    Check test and get loop    ${TEST NAME}    1
    Should be IN ENUMERATE loop    ${loop}           2
    Should be loop iteration       ${loop.kws[0]}    \${x} = 0, \${i1} = a, \${i2} = b, \${i3} = c, \${i4} = d, \${i5} = e
    Should be loop iteration       ${loop.kws[1]}    \${x} = 1, \${i1} = f, \${i2} = g, \${i3} = h, \${i4} = i, \${i5} = j

One variable only
    ${loop} =    Check test and get loop    ${TEST NAME}
    Should be IN ENUMERATE loop    ${loop}           3
    Should be loop iteration       ${loop.kws[0]}    \${item} = (0, ${u}'a')
    Should be loop iteration       ${loop.kws[1]}    \${item} = (1, ${u}'b')

Wrong number of variables
    Check test and failed loop    ${TEST NAME}    IN ENUMERATE
