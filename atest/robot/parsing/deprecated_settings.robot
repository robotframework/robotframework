*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    parsing/deprecated_settings.robot
Resource         atest_resource.robot

*** Test Cases ***
Suite Document
    Should be equal    ${SUITE.doc}    This is deprecated since RF 3.0.\nUse *Documentation* instead.
    Setting is deprecated    0    Document    Documentation

Test [Document]
    ${tc} =    Check test case    Test Case
    Should be equal    ${tc.doc}    This too is deprecated.
    Test setting is deprecated    5    document    Documentation

Keyword [Document]
    ${tc} =    Check test case    Test Case
    Should be equal    ${tc.kws[0].doc}    And so is this.
    Keyword setting is deprecated    8    DOC U MENT    Documentation

Suite Precondition
    Check Log Message    ${SUITE.setup.msgs[0]}    Suite Pre is deprecated
    Setting is deprecated    1    Suite Precondition    Suite Setup

Suite Postcondition
    Check Log Message    ${SUITE.teardown.msgs[0]}    Suite Post is deprecated
    Setting is deprecated    2    Suite Post Cond IT Ion    Suite Teardown

Test Precondition
    ${tc} =    Check test case    Defaults
    Check Log Message    ${tc.setup.msgs[0]}    Test Pre is deprecated
    Setting is deprecated    3    Test Precondition    Test Setup

Test Postcondition
    ${tc} =    Check test case    Defaults
    Check Log Message    ${tc.teardown.msgs[0]}    Test Post is deprecated
    Setting is deprecated    4    testpostcondition    Test Teardown

[Precondition]
    ${tc} =    Check test case    Test Case
    Check Log Message    ${tc.setup.msgs[0]}    [Pre] is deprecated
    Test setting is deprecated    6    Pre Condition    Setup

[Postcondition]
    ${tc} =    Check test case    Test Case
    Check Log Message    ${tc.teardown.msgs[0]}    [Post] is deprecated
    Test setting is deprecated    7    postcondition    Teardown

*** Keywords ***
Setting is deprecated
    [Arguments]    ${index}    ${deprecated}    ${instead}    @{extra}
    ${path} =    Normalize Path    ${DATADIR}/parsing/deprecated_settings.robot
    ${message} =    Catenate
    ...    Error in file '${path}':
    ...    @{extra}
    ...    Setting '${deprecated}' is deprecated. Use '${instead}' instead.
    Check Log Message      @{ERRORS}[${index}]    ${message}    WARN

Test setting is deprecated
    [Arguments]    ${index}    ${deprecated}    ${instead}
    Setting is deprecated    ${index}    ${deprecated}    ${instead}
    ...    Invalid syntax in test case 'Test Case':

Keyword setting is deprecated
    [Arguments]    ${index}    ${deprecated}    ${instead}
    Setting is deprecated    ${index}    ${deprecated}    ${instead}
    ...    Invalid syntax in keyword 'Keyword':
