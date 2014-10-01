*** Setting ***
Library           OperatingSystem

*** Variable ***
${envvar}         EXAMPLE_ENV_VAR_32FDHT

*** Test Case ***
Get Environment Variable
    [Documentation]    FAIL Environment variable 'NON_EXISTING_AL4ALKD' doesn't exist
    ${env}    Get Environment Variable    PATH
    Fail Unless    ${env.count('${:}')} > 0
    ${env}    Get Environment Variable    NON_EXISTING_ALKTWHJE    this is default
    Equals    ${env}    this is default
    ${env}    Get Environment Variable    NON_EXISTING_AL4ALKD    # this keyword fails

Set Environment Variable
    Set Environment Variable    ${envvar}    Hello
    Env Var Is    ${envvar}    Hello
    Set Environment Variable    ${envvar}    Moi
    Env Var Is    ${envvar}    Moi

Delete Environment Variable
    [Documentation]    FAIL Environment variable 'EXAMPLE_ENV_VAR_32FDHT' doesn't exist
    [Setup]    Set Environment Variable    ${envvar}    Hello
    Delete Environment Variable    ${envvar}
    Environment Variable Is Not Set    ${envvar}
    Delete Environment Variable    ${envvar}    # should not fail
    Get Environment Variable    ${envvar}

Environment Variable Is Set
    [Documentation]    FAIL Environment variable 'EXAMPLE_ENV_VAR_32FDHT' is not set
    [Setup]    Set Environment Variable    ${envvar}    Hello
    Environment Variable Is Set    ${envvar}
    Delete Environment Variable    ${envvar}
    Environment Variable Is Set    ${envvar}

Environment Variable Is Not Set
    [Documentation]    FAIL Environment variable 'EXAMPLE_ENV_VAR_32FDHT' is set
    [Setup]    Delete Environment Variable    ${envvar}
    Environment Variable Is Not Set    ${envvar}
    Set Environment Variable    ${envvar}    Hello
    Environment Variable Is Not Set    ${envvar}

Set Environment Variable In One Test And Use In Another, Part 1
    [Documentation]    Environment variable is set in this test case and used in Part 2
    Set Environment Variable    ${envvar}    Hello another test case!

Set Environment Variable In One Test And Use In Another, Part 2
    [Documentation]    Environment variable was set in Part 1 and used here
    Env Var Is    ${envvar}    Hello another test case!

*** Keyword ***
Env Var Is
    [Arguments]    ${name}    ${expected}
    ${env}    Get Environment Variable    ${name}
    Equals    ${env}    ${expected}
