*** Setting ***
Documentation     Tests for set variable and set test/suite/global variable keywords
Suite Setup       Run Tests    --variable cli_var_1:CLI1 --variable cli_var_2:CLI2 --variable cli_var_3:CLI3
...    standard_libraries/builtin/setting_variables
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Case ***
Set Variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = Hello

Set Variable With More Or Less Than One Value
    ${tc} =    Check Test Case    ${TESTNAME}

Set Test Variable - Scalars
    Check Test Case    ${TESTNAME}

Set Test Variable - Lists
    Check Test Case    ${TESTNAME}

Set Test Variable - Dicts
    Check Test Case    ${TESTNAME}

Dict Set To Scalar Is Dot Accessible
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Set Test Variable Needing Escaping
    Check Test Case    ${TESTNAME}

Set Test Variable In User Keyword
    Check Test Case    ${TESTNAME}

Set Test Variable Not Affecting Other Tests
    Check Test Case    ${TESTNAME}

Test Variables Set In One Suite Are Not Available In Another
    Check Test Case    ${TESTNAME}

Set Suite Variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Suite Teardown Passed

Suite Variables Set In One Suite Are Not Available In Another
    Check Test Case    ${TESTNAME}

Set Child Suite Variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Set Global Variables
    Check Test Case    Set Global Variable 1
    Check Test Case    Set Global Variable 2
    Check Suite Teardown Passed

Global Variables Set In One Suite Are Not Available In Another
    Check Test Case    ${TESTNAME}

Scopes And Overriding
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Overiding Variable When It Has Non-string Value
    Check Test Case    ${TEST NAME}

Set Test/Suite/Global Variables With Normal Variable Syntax
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Set Test/Suite/Global Variable Using Empty List Variable
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Set Test/Suite/Global Variable Using Empty Dict Variable
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Set Test/Suite/Global Variable In User Keyword When Variable Name Is Used As Argument
    Check Test Case    ${TEST NAME}

Setting Test/Suite/Global Variable Which Value Is In Variable Like Syntax
    Check Test Case    ${TEST NAME}

Setting Test/Suite/Global Variable Which Value Is In Variable Syntax
    Check Test Case    ${TEST NAME}

Set Test/Suite/Global Variable With Internal Variables In Name
    [Documentation]    This obscure test is here to prevent this bug from reappearing:
    ...                http://code.google.com/p/robotframework/issues/detail?id=397
    Check Test Case    ${TEST NAME}

Mutating scalar variable set using `Set Test/Suite/Global Variable` keywords
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3

Mutating list variable set using `Set Test/Suite/Global Variable` keywords
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3

Mutating dict variable set using `Set Test/Suite/Global Variable` keywords
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3

Using @{EMPTY} with `Set Test/Suite/Global Variable` keywords
    Check Test Case    ${TEST NAME}
    Check Test Case    ${TEST NAME} 2

If setting test/suite/global variable fails, old value is preserved
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3
    Check Test Case    ${TEST NAME} 4

Setting non-dict value to test/suite/global level dict variable
    Check Test Case    ${TEST NAME} - test
    Check Test Case    ${TEST NAME} - suite
    Check Test Case    ${TEST NAME} - global

Setting scalar test variable with list value is not possible
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Setting scalar suite variable with list value is not possible
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Setting scalar global variable with list value is not possible
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

*** Keyword ***
Check Suite Teardown Passed
    ${suite} =    Get Test Suite    Variables
    Should Be Equal    ${suite.teardown.status}    PASS
