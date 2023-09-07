*** Settings ***
Suite Setup       My Setup
Suite Teardown    My Teardown
Resource          resource.robot

*** Test Cases ***
Test 2.1
    Register All    Test 2.1
    libraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2    Test 2.1
    libraryscope.Suite.Should Be Registered    Suite 2    Test 2.1
    libraryscope.Test.Should Be Registered    Test 2.1
    Invalids Should Have Registered    Test 2.1

Test 2.2
    Register All    Test 2.2
    libraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2    Test 2.1
    ...    Test 2.2
    libraryscope.Suite.Should Be Registered    Suite 2    Test 2.1    Test 2.2
    libraryscope.Test.Should Be Registered    Test 2.2
    Invalids Should Have Registered    Test 2.2

*** Keywords ***
My Setup
    Register All    Suite 2
    libraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2
    libraryscope.Suite.Should Be Registered    Suite 2
    libraryscope.Test.Should Be Registered    Suite 2
    Invalids Should Have Registered    Suite 2

My Teardown
    libraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2    Test 2.1
    ...    Test 2.2
    libraryscope.Suite.Should Be Registered    Suite 2    Test 2.1    Test 2.2
    libraryscope.Test.Should Be Registered    Suite 2
    Invalids Should Have Registered    Suite 2
