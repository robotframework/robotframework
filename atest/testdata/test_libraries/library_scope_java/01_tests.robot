*** Setting ***
Suite Setup       My Setup
Suite Teardown    My Teardown
Resource          resource.robot

*** Test Case ***
Test 1.1
    Register All    Test 1.1
    javalibraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1
    javalibraryscope.Suite.Should Be Registered    Suite 1    Test 1.1
    javalibraryscope.Test.Should Be Registered    Test 1.1
    Invalids Should Have Registered    Test 1.1

Test 1.2
    Register All    Test 1.2
    javalibraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2
    javalibraryscope.Suite.Should Be Registered    Suite 1    Test 1.1    Test 1.2
    javalibraryscope.Test.Should Be Registered    Test 1.2
    Invalids Should Have Registered    Test 1.2

*** Keyword ***
My Setup
    Register All    Suite 1
    javalibraryscope.Global.Should Be Registered    Suite 0    Suite 1
    javalibraryscope.Suite.Should Be Registered    Suite 1
    javalibraryscope.Test.Should Be Registered    Suite 1
    Invalids Should Have Registered    Suite 1

My Teardown
    javalibraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2
    javalibraryscope.Suite.Should Be Registered    Suite 1    Test 1.1    Test 1.2
    javalibraryscope.Test.Should Be Registered    Suite 1
    Invalids Should Have Registered    Suite 1
