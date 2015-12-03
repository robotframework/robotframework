*** Setting ***
Resource          atest_resource.robot

*** Test Case ***
Python Library Scopes
    Run Tests    sources=test_libraries/library_scope
    Check Test Case    Test 1.1
    Check Test Case    Test 1.2
    Check Test Case    Test 2.1
    Check Test Case    Test 2.2

Java Library Scopes
    [Tags]    require-jython
    Run Tests    sources=test_libraries/library_scope_java
    Check Test Case    Test 1.1
    Check Test Case    Test 1.2
    Check Test Case    Test 2.1
    Check Test Case    Test 2.2
