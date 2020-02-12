*** Settings ***
Documentation   Tests for libraries using getKeywordNames and runKeyword with **kwargs functionality. In these tests libraries are implemented with Java.
Suite Setup     Run Tests  ${EMPTY}  test_libraries/dynamic_kwargs_support_java.robot
Force Tags      require-jython
Resource        atest_resource.robot

*** Test Cases ***
Run Keyword
    Check Test Case  ${TESTNAME}

Documentation and Argument Boundaries Work With Kwargs In Java
    Check test case and its keyword  Java Kwargs  key:value

Documentation and Argument Boundaries Work With Varargs and Kwargs In Java
    Check test case and its keyword  Java Varargs and Kwargs  1 2 3 key:value

Only one runkeyword implementation
    Check Test Case  ${TESTNAME}

Default values
    Check Test Case  ${TESTNAME}

Named arguments
    Check Test Case  ${TESTNAME}

*** Keywords ***
Check test case and its keyword
    [Arguments]  ${keyword}  ${args}
    ${tc} =  Check Test case  ${TESTNAME}
    Should Be Equal  ${tc.kws[0].doc}  Keyword documentation for ${keyword}
    Check Log Message  ${tc.kws[0].msgs[0]}  Executed keyword ${keyword} with arguments ${args}
