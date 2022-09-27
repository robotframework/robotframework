*** Settings ***
Suite Setup     Run Tests    --loglevel DEBUG    standard_libraries/builtin/call_method.robot
Resource        atest_resource.robot

*** Test Cases ***
Call Method
    Check Test Case  ${TEST NAME}

Call Method Returns
    Check Test Case  ${TEST NAME}

Called Method Fails
    ${tc} =    Check Test Case  ${TEST NAME}
    Check Log Message    ${tc.body[0].msgs[0]}    Calling method 'my_method' failed: Expected failure    FAIL
    ${error} =    Catenate    SEPARATOR=\n
    ...    RuntimeError: Expected failure
    ...
    ...    The above exception was the direct cause of the following exception:
    ...
    ...    RuntimeError: Calling method 'my_method' failed: Expected failure
    Traceback Should Be    ${tc.body[0].msgs[1]}
    ...    standard_libraries/builtin/objects_for_call_method.py    my_method    raise RuntimeError('Expected failure')
    ...    error=${error}

Call Method With Kwargs
    Check Test Case  ${TEST NAME}

Equals in non-kwargs must be escaped
    Check Test Case  ${TEST NAME}

Call Method From Module
    Check Test Case  ${TEST NAME}

Call Non Existing Method
    Check Test Case  ${TEST NAME}
