*** Settings ***
Suite Setup       My Setup
Suite Teardown    My Teardown
Resource          resource.robot

*** Keywords ***
My Setup
    Register All    Suite 0
    libraryscope.Global.Should Be Registered    Suite 0
    libraryscope.Suite.Should Be Registered    Suite 0
    libraryscope.Test.Should Be Registered    Suite 0
    Invalids Should Have Registered    Suite 0

My Teardown
    libraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2    Test 2.1
    ...    Test 2.2
    libraryscope.Suite.Should Be Registered    Suite 0
    libraryscope.Test.Should Be Registered    Suite 0
    Invalids Should Have Registered    Suite 0
