*** Settings ***
Suite Setup       My Setup
Suite Teardown    My Teardown
Resource          resource.robot

*** Test Cases ***
Test 1.1
    Register All    Test 1.1
    libraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1
    libraryscope.Suite.Should Be Registered    Suite 1    Test 1.1
    libraryscope.Test.Should Be Registered    Test 1.1
    Invalids Should Have Registered    Test 1.1

Test 1.2
    Register All    Test 1.2
    libraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2
    libraryscope.Suite.Should Be Registered    Suite 1    Test 1.1    Test 1.2
    libraryscope.Test.Should Be Registered    Test 1.2
    Invalids Should Have Registered    Test 1.2

*** Keywords ***
My Setup
    Register All    Suite 1
    libraryscope.Global.Should Be Registered    Suite 0    Suite 1
    libraryscope.Suite.Should Be Registered    Suite 1
    libraryscope.Test.Should Be Registered    Suite 1
    Invalids Should Have Registered    Suite 1

My Teardown
    libraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2
    libraryscope.Suite.Should Be Registered    Suite 1    Test 1.1    Test 1.2
    libraryscope.Test.Should Be Registered    Suite 1
    Invalids Should Have Registered    Suite 1
