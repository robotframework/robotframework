*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/env_config.robot
Resource         atest_resource.robot

*** Test Cases ***
By default environ is got from system
    Check Test Case    ${TESTNAME}

Giving whole environ
    Check Test Case    ${TESTNAME}

Giving individual values
    Check Test Case    ${TESTNAME}

Giving multiple values separately
    Check Test Case    ${TESTNAME}

Invividually given overrides system variable
    Check Test Case    ${TESTNAME}

Invividually given overrides value in given environ
    Check Test Case    ${TESTNAME}

Non-ASCII value
    Check Test Case    ${TESTNAME}

Secret in environment variable via env Dict
    ${tc} =    Check Test Case    ${TESTNAME}
    # TODO: Fix the below test
    #Check Log Message    ${tc[0, 1]}    *env:${SPACE*5}<env with secrets>*    DEBUG    pattern=yes

Secret in environment variable via env:name Syntax
    ${tc} =    Check Test Case    ${TESTNAME}
    # TODO: Fix the below test
    #Check Log Message    ${tc[0, 1]}    *env:${SPACE*5}<env with secrets>*    DEBUG    pattern=yes

Multiple Secrets in environment variables
    ${tc} =    Check Test Case    ${TESTNAME}
    # TODO: Fix the below test
    #Check Log Message    ${tc[0, 1]}    *env:${SPACE*5}<env with secrets>*    DEBUG    pattern=yes
