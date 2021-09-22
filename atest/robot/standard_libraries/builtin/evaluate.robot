*** Settings ***
Suite Setup       Run Keywords
...               Remove Environment Variable    PYTHONCASEOK    AND
...               Run Tests    ${EMPTY}    standard_libraries/builtin/evaluate.robot
Suite Teardown    Set Environment Variable    PYTHONCASEOK    True
Resource          atest_resource.robot

*** Test Cases ***
Evaluate
    Check Test Case    ${TESTNAME}

Modules are imported automatically
    Check Test Case    ${TESTNAME}

Importing non-existing module fails with NameError
    Check Test Case    ${TESTNAME}

Importing invalid module fails with original error
    Check Test Case    ${TESTNAME}

Automatic module imports are case-sensitive
    Check Test Case    ${TESTNAME}

Automatic modules don't override builtins
    Check Test Case    ${TESTNAME}

Explicit modules
    Check Test Case    ${TESTNAME}

Explicit modules are needed with nested modules
    Check Test Case    ${TESTNAME}

Explicit modules can override builtins
    Check Test Case    ${TESTNAME}

Explicit modules used in lambda
    Check Test Case    ${TESTNAME}

Custom namespace
    Check Test Case    ${TESTNAME}

Custom namespace is case-sensitive
    Check Test Case    ${TESTNAME}

Custon namespace used in lambda
    Check Test Case    ${TESTNAME}

Namespace from Get Variables
    Check Test Case    ${TESTNAME}

Non-dict namespace
    Check Test Case    ${TESTNAME}

Variables are available automatically
    Check Test Case    ${TESTNAME}

Automatic variables don't work in strings
    Check Test Case    ${TESTNAME}

Automatic variables don't override Python built-ins
    Check Test Case    ${TESTNAME}

Automatic variables don't override custom namespace
    Check Test Case    ${TESTNAME}

Automatic variables don't override modules
    Check Test Case    ${TESTNAME}

Automatic variables are case and underscore insensitive
    Check Test Case    ${TESTNAME}

Automatic variable from variable
    Check Test Case    ${TESTNAME}

Non-existing automatic variable
    Check Test Case    ${TESTNAME}

Non-existing automatic variable with recommendation
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Invalid expression
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3
    Check Test Case    ${TESTNAME} 4
    Check Test Case    ${TESTNAME} 5
    Check Test Case    ${TESTNAME} 6
    Check Test Case    ${TESTNAME} 7
    Check Test Case    ${TESTNAME} 8

Invalid $ usage
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3
    Check Test Case    ${TESTNAME} 4
    Check Test Case    ${TESTNAME} 5
    Check Test Case    ${TESTNAME} 6
    Check Test Case    ${TESTNAME} 7
    Check Test Case    ${TESTNAME} 8

Evaluate Empty
    Check Test Case    ${TESTNAME}

Evaluate Nonstring
    Check Test Case    ${TESTNAME}

Evaluate doesn't see module globals
    Check Test Case    ${TESTNAME}

Evaluation errors can be caught
    Check Test Case    ${TESTNAME}
