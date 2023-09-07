*** Settings ***
Documentation     Normal test cases
Suite Setup       Log    Setup
Suite Teardown    No operation
Force Tags        f1
Default Tags      d1    d2
Metadata          Something    My Value

*** Test Cases ***
First
    [Tags]    t1    t2
    Log    Test 1

Second One
    Log    Test 2

Third One
    Log    Test 3

Fourth One With More Complex Name
    Log    Test 4

Fifth
    Log    Test 5

GlobTestCase1
    Log    GlobTestCase1

GlobTestCase2
    Log    GlobTestCase2

GlobTestCase3
    Log    GlobTestCase3

GlobTestCase[5]
    Log    GlobTestCase[5]

GlobTest Cat
    Log    Cat

GlobTest Rat
    Log    Cat
