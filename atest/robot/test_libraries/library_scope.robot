*** Setting ***
Resource          atest_resource.robot

*** Variable ***

*** Test Case ***
Python Library Scopes
    [Documentation]    All different library scopes (global, suite and test) are tested as well as invalid scopes (defaulting to test scope). Using libraries written with Python.
    Run Tests    \    test_libraries${/}library_scope
    Check Test Case    Test 1.1
    Check Test Case    Test 1.2
    Check Test Case    Test 2.1
    Check Test Case    Test 2.2

Java Library Scopes
    [Documentation]    Same as Python Library Scopes but with Java libraries
    [Tags]    require-jython
    Run Tests    \    test_libraries${/}library_scope_java
    Check Test Case    Test 1.1
    Check Test Case    Test 1.2
    Check Test Case    Test 2.1
    Check Test Case    Test 2.2
