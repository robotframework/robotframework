*** Setting ***
Suite Setup       My Setup
Suite Teardown    My Teardown
Resource          resource.robot

*** Test Case ***
Test 2.1
    Register All    Test 2.1
    javalibraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2    Test 2.1
    javalibraryscope.Suite.Should Be Registered    Suite 2    Test 2.1
    javalibraryscope.Test.Should Be Registered    Test 2.1
    Invalids Should Have Registered    Test 2.1

Test 2.2
    Register All    Test 2.2
    javalibraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2    Test 2.1
    ...    Test 2.2
    javalibraryscope.Suite.Should Be Registered    Suite 2    Test 2.1    Test 2.2
    javalibraryscope.Test.Should Be Registered    Test 2.2
    Invalids Should Have Registered    Test 2.2

*** Keyword ***
My Setup
    Register All    Suite 2
    javalibraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2
    javalibraryscope.Suite.Should Be Registered    Suite 2
    javalibraryscope.Test.Should Be Registered    Suite 2
    Invalids Should Have Registered    Suite 2

My Teardown
    javalibraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2    Test 2.1
    ...    Test 2.2
    javalibraryscope.Suite.Should Be Registered    Suite 2    Test 2.1    Test 2.2
    javalibraryscope.Test.Should Be Registered    Suite 2
    Invalids Should Have Registered    Suite 2
