*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/dynamic_library_args_and_docs.robot
Test Template     Check test case and its doc
Resource          atest_resource.robot

*** Test Cases ***
Documentation And Argument Boundaries Work With No Args
    Keyword documentation for No Arg

Documentation And Argument Boundaries Work With Mandatory Args
    Keyword documentation for One Arg

Documentation And Argument Boundaries Work With Default Args
    Keyword documentation for One or Two Args
    ...    Executed keyword "One or Two Args" with arguments ('1',).
    ...    Executed keyword "One or Two Args" with arguments ('1', '2').

Default value as tuple
    Keyword documentation for Default as tuple
    ...    Executed keyword "Default as tuple" with arguments ('1',).
    ...    Executed keyword "Default as tuple" with arguments ('1', '2').
    ...    Executed keyword "Default as tuple" with arguments ('1', '2', '3').
    ...    Executed keyword "Default as tuple" with arguments ('1', False, '3').
    ...    Executed keyword "Default as tuple" with arguments ('1', False, '3').

Documentation And Argument Boundaries Work With Varargs
    Keyword documentation for Many Args

Documentation and Argument Boundaries Work When Argspec is None
    Keyword documentation for No Arg Spec

Multiline Documentation
    Multiline\nshort doc!

Keyword Not Created And Warning Shown When Getting Documentation Fails
    [Template]    Check Creating Keyword Failed Due To Invalid Doc Message
    0    Default as tuple
    1    Many Args
    2    Multiline
    3    No Arg
    4    No Arg Spec
    5    One Arg
    6    One or Two Args
    [Teardown]    Check Log Message    ${ERRORS}[7]
    ...    Imported library 'classes.InvalidGetDocDynamicLibrary' contains no keywords.    WARN

Keyword Not Created And Warning Shown When Getting Arguments Fails
    [Template]    Check Creating Keyword Failed Due To Invalid Args Message
    8    Default as tuple
    9    Many Args
    10   Multiline
    11   No Arg
    12   No Arg Spec
    13   One Arg
    14   One or Two Args
    [Teardown]    Check Log Message    ${ERRORS}[15]
    ...    Imported library 'classes.InvalidGetArgsDynamicLibrary' contains no keywords.    WARN

*** Keywords ***
Check test case and its doc
    [Arguments]    ${expected doc}    @{msgs}
    ${tc} =    Check Test case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].doc}    ${expected doc}
    FOR    ${kw}    ${msg}    IN ZIP    ${tc.kws}    ${msgs}
        Check Log Message    ${kw.msgs[0]}    ${msg}
    END

Check Creating Keyword Failed Due To Invalid Doc Message
    [Arguments]    ${index}    ${kw}
    Check Creating Keyword Failed Message    ${index}    ${kw}
    ...    classes.InvalidGetDocDynamicLibrary
    ...    Calling dynamic method 'get_keyword_documentation' failed: TypeError: *

Check Creating Keyword Failed Due To Invalid Args Message
    [Arguments]    ${index}    ${kw}
    Check Creating Keyword Failed Message    ${index}    ${kw}
    ...    classes.InvalidGetArgsDynamicLibrary
    ...    Calling dynamic method 'get_keyword_arguments' failed: ZeroDivisionError: *

Check Creating Keyword Failed Message
    [Arguments]    ${index}    ${kw}    ${lib}    @{error}
    Error In Library    ${lib}
    ...    Adding keyword '${kw}' failed:
    ...    @{error}
    ...    pattern=True
    ...    index=${index}
