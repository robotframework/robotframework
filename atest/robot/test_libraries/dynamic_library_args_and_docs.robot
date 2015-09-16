*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/dynamic_library_args_and_docs.robot
Test Template   Check test case and its doc
Resource        atest_resource.robot

*** Test Cases ***
Documentation And Argument Boundaries Work With No Args
    Keyword documentation for No Arg

Documentation And Argument Boundaries Work With Mandatory Args
    Keyword documentation for One Arg

Documentation And Argument Boundaries Work With Default Args
    Keyword documentation for One or Two Args

Documentation And Argument Boundaries Work With Varargs
    Keyword documentation for Many Args

Documentation and Argument Boundaries Work When Argspec is None
    Keyword documentation for No Arg Spec

Keyword Not Created And Warning Shown When Getting Documentation Fails
    [Template]  Check Creating Keyword Failed Due To Invalid Doc Message
    0  Many Args
    1  No Arg
    3  One Arg
    4  One or Two Args
    [Teardown]  Check Log Message  ${ERRORS.msgs[5]}   Imported library 'classes.InvalidGetDocDynamicLibrary' contains no keywords  WARN

Keyword Not Created And Warning Shown When Getting Arguments Fails
    [Template]  Check Creating Keyword Failed Due To Invalid Args Message
    6  Many Args
    7  No Arg
    9  One Arg
    10  One or Two Args
    [Teardown]  Check Log Message  ${ERRORS.msgs[11]}   Imported library 'classes.InvalidGetArgsDynamicLibrary' contains no keywords  WARN

Documentation And Argument Boundaries Work With No Args In Java
    [Tags]  require-jython
    Keyword documentation for Java No Arg

Documentation And Argument Boundaries Work With Mandatory Args In Java
    [Tags]  require-jython
    Keyword documentation for Java One Arg

Documentation And Argument Boundaries Work With Default Args In Java
    [Tags]  require-jython
    Keyword documentation for Java One or Two Args

Documentation And Argument Boundaries Work With Varargs In Java
    [Tags]  require-jython
    Keyword documentation for Java Many Args

Keyword With Kwargs Not Created And Warning Shown When No Run Keyword With Kwargs Support In Java
    [Tags]  require-jython
    [Template]  NONE
    Check Log Message  ${ERRORS.msgs[12]}  Adding keyword 'Unsupported Java Kwargs' to library 'ArgDocDynamicJavaLibrary' failed: Too few 'runKeyword' method parameters for **kwargs support.  ERROR

Keyword Not Created And Warning Shown When Getting Documentation Fails In Java
    [Tags]  require-jython
    [Template]  NONE
    Check Log Message  ${ERRORS.msgs[13]}  Adding keyword 'Invalid Java Args' to library 'ArgDocDynamicJavaLibrary' failed: Calling dynamic method 'getKeywordArguments' failed: Get args failure  ERROR

Keyword Not Created And Warning Shown When Getting Arguments Fails In Java
    [Tags]  require-jython
    [Template]  NONE
    Check Log Message  ${ERRORS.msgs[14]}  Adding keyword 'Invalid Java Doc' to library 'ArgDocDynamicJavaLibrary' failed: Calling dynamic method 'getKeywordDocumentation' failed: Get doc failure  ERROR


*** Keywords ***

Check test case and its doc
    [Arguments]  ${expected doc}
    ${tc} =  Check Test case  ${TESTNAME}
    Should Be Equal  ${tc.kws[0].doc}  ${expected doc}

Check Creating Keyword Failed Due To Invalid Doc Message
    [Arguments]  ${index}  ${kw}
    ${lib} =  Set Variable  classes.InvalidGetDocDynamicLibrary
    ${err} =  Set Variable  Calling dynamic method 'get_keyword_documentation' failed: TypeError:
    Check Creating Keyword Failed Message  ${index}  ${kw}  ${lib}  ${err}

Check Creating Keyword Failed Due To Invalid Args Message
    [Arguments]  ${index}  ${kw}
    ${lib} =  Set Variable  classes.InvalidGetArgsDynamicLibrary
    ${err} =  Set Variable  Calling dynamic method 'get_keyword_arguments' failed: ZeroDivisionError:
    Check Creating Keyword Failed Message  ${index}  ${kw}  ${lib}  ${err}

Check Creating Keyword Failed Message
    [Arguments]  ${index}  ${kw}  ${lib}  ${error}
    ${msg} =  Set Variable  Adding keyword '${kw}' to library '${lib}' failed: ${error} *
    Check Log Message  ${ERRORS.msgs[${index}]}  ${msg}  ERROR  pattern=yes
