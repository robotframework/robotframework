*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/named_args/variables_in_names.robot
Resource         atest_resource.robot

*** Test Cases ***
Named arg name as variable
    Check Test Case    ${TESTNAME}

Named arg containing variable
    Check Test Case    ${TESTNAME}

Kwargs with variables in names
    Check Test Case    ${TESTNAME}

Kwargs with variables with non-ASCII value in names
    Check Test Case    ${TESTNAME}

Escaping variable syntax in kwarg names
    Check Test Case    ${TESTNAME}

Named args and kwargs with variables
    Check Test Case    ${TESTNAME}

Non-existing variable as named arg name
    Check Test Case    ${TESTNAME}

Non-existing variable as kwargs name
    Check Test Case    ${TESTNAME}

Variable with non-string value as named arg name
    Check Test Case    ${TESTNAME}

Variable with non-string value as kwargs name
    Check Test Case    ${TESTNAME}

Equal sign in variable name
    Check Test Case    ${TESTNAME}
