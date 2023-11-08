*** Settings ***
Documentation     Tests for set variable and set test/suite/global variable keywords
Suite Setup       Run Tests
...               --variable cli_var_1:CLI1 --variable cli_var_2:CLI2 --variable cli_var_3:CLI3
...               standard_libraries/builtin/setting_variables
Resource          atest_resource.robot

*** Test Cases ***
Set Variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    \${var} = Hello

Set Variable With More Or Less Than One Value
    Check Test Case    ${TESTNAME}

Set Local Variable - Scalars
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    \${scalar} = Hello world

Set Local Variable - Lists
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[3].msgs[0]}    \@{list} = [ One | Two | Three ]
    Check Log Message    ${tc.kws[6].msgs[0]}    \@{list} = [ 1 | 2 | 3 ]

Set Local Variable - Dicts
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[4].msgs[0]}    \&{DICT} = { a=1 | 2=b }

Set Local Variables Overrides Test Variables
    Check Test Case    ${TESTNAME}

Set Local Variable In Keyword Not Available In Test
    Check Test Case    ${TESTNAME}

Set Local Variable In Keyword Not Available In Another Keyword
    Check Test Case    ${TESTNAME}

Setting Local Variable In Test Not Available In Keyword
    Check Test Case    ${TESTNAME}

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

Set Test Variable Affect Subsequent Keywords
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].doc}    Makes a variable available everywhere within the scope of the current test.

Set Test Variable In User Keyword
    Check Test Case    ${TESTNAME}

Set Test Variable Not Affecting Other Tests
    Check Test Case    ${TESTNAME}

Test Variables Set In One Suite Are Not Available In Another
    Check Test Case    ${TESTNAME}

Set Test Variable cannot be used in suite setup or teardown
    Check Test Case    ${TESTNAME}

Set Task Variable as alias for Set Test Variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].doc}    Makes a variable available everywhere within the scope of the current task.

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

Global Variables Set In One Suite Are Available In Another
    Check Test Case    ${TESTNAME}

Global Variable Set In One Suite Overrides Variable In Variable Table
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
    ...                https://github.com/robotframework/robotframework/issues/397
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

Using \@{EMPTY} with `Set Test/Suite/Global Variable` keywords
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

*** Keywords ***
Check Suite Teardown Passed
    ${suite} =    Get Test Suite    Variables
    Should Be Equal    ${suite.teardown.status}    PASS
