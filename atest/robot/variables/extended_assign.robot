*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/extended_assign.robot
Resource         atest_resource.robot

*** Test Cases ***
Set attributes to Python object
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${VAR.attr} = new value
    Check Log Message    ${tc.kws[1].msgs[0]}    \${ v a r . attr2 } = nv2

Set nested attribute
    Check Test Case    ${TESTNAME}

Set nested attribute when parent uses item access
    Check Test Case    ${TESTNAME}

Trying to set un-settable attribute
    Check Test Case    ${TESTNAME}

Un-settable attribute error is catchable
    Check Test Case    ${TESTNAME}

Using extended syntax when base variable does not exists creates new variable
    Check Test Case    ${TESTNAME}

Overriding variable that has dot it its name is possible
    Check Test Case    ${TESTNAME}

Strings and integers do not support extended assign
    Check Test Case    ${TESTNAME}

Attribute name must be valid
    Check Test Case    ${TESTNAME}

Extended syntax is ignored with list variables
    Check Test Case    ${TESTNAME}
