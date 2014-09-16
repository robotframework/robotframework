*** Setting ***
Suite Setup       My Setup
Suite Teardown    My Teardown
Resource          resource.robot

*** Keyword ***
My Setup
    Register All    Suite 0
    javalibraryscope.Global.Should Be Registered    Suite 0
    javalibraryscope.Suite.Should Be Registered    Suite 0
    javalibraryscope.Test.Should Be Registered    Suite 0
    Invalids Should Have Registered    Suite 0

My Teardown
    javalibraryscope.Global.Should Be Registered    Suite 0    Suite 1    Test 1.1    Test 1.2    Suite 2    Test 2.1
    ...    Test 2.2
    javalibraryscope.Suite.Should Be Registered    Suite 0
    javalibraryscope.Test.Should Be Registered    Suite 0
    Invalids Should Have Registered    Suite 0
