*** Settings ***
Documentation     Unit test suite to Utils.Report_Failure_Due_To_Bug keyword.

*** Test cases ***
Message_Contains_Reported_Bug
    Pass_Execution    Initial Test Message
    [Teardown]    Check_Test_Message_Behavior

*** Keywords ***
Check_Test_Message_Behavior
    Should_Be_Equal    ${TEST_MESSAGE}    Initial Test Message
    BuiltIn.Set_Test_Message    First    True
    Should_Be_Equal    ${TEST_MESSAGE}    Initial Test Message First
    BuiltIn.Set_Test_Message    Other
    Should_Be_Equal    ${TEST_MESSAGE}    Other
    BuiltIn.Set_Test_Message    Second    True
    Should_Be_Equal    ${TEST_MESSAGE}    Other Second
