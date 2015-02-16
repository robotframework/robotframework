*** Settings ***
Documentation   %{PATH} used in suite documentation
Suite Setup     Set Environment Variable  THIS_ENV_VAR_IS_SET  Env var value
Default Tags    %{PATH}
Metadata        PATH    %{PATH}
Library         OperatingSystem

*** Variables ***
${SCALAR PATH}  %{PATH}
@{LIST PATH}    %{PATH}

*** Test Cases ***
Environment Variables In Keyword Argument
    Should Be Equal  %{THIS_ENV_VAR_IS_SET}  Env var value
    Should Be Equal  %{THIS_ENV_VAR_IS_SET} can be catenated. PATH: %{PATH}  Env var value can be catenated. PATH: %{PATH}

Java System Properties Can Be Used
    Should Be Equal  %{file.separator}  ${/}
    Should Not Be Empty  %{os.name}

Non-ASCII Environment Variable
    Set Environment Variable  nön_äsĉïï   äëïöüÿ
    Should Be Equal  %{nön_äsĉïï}  äëïöüÿ
    [Teardown]  Remove Environment Variable  nön_äsĉïï

Environment Variable With Backslashes
    Set Environment Variable  ENV_VAR_WITH_BACKSLASHES  c:\\temp\\backslash
    Should Be Equal  %{ENV_VAR_WITH_BACKSLASHES}  c:\\temp\\backslash

Environment Variable With Internal Variables
    Set Environment Variable  yet_another_env_var  THIS_ENV_VAR
    ${normal_var} =  Set Variable  IS_SET
    Should Be Equal  %{%{yet_another_env_var}_${normal_var}}  Env var value

Non-Existing Environment Variable
    [Documentation]  FAIL Environment variable '%{NON_EXISTING}' not found.
    Log  %{NON_EXISTING}

Environment Variables Are Case Sensitive
    [Documentation]  FAIL Environment variable '%{this_env_var_is_set}' not found. Did you mean:
    ...    ${SPACE * 4}\%{THIS_ENV_VAR_IS_SET}
    Log  %{this_env_var_is_set}

Environment Variables Are Not Case Sensitive On Windows
    [Documentation]  On Windows case is not sensitive.
    Log  %{this_env_var_is_set}

Environment Variables Are Space Sensitive 1
    [Documentation]  FAIL Environment variable '%{THIS ENV VAR IS SET}' not found. Did you mean:
    ...    ${SPACE * 4}\%{THIS_ENV_VAR_IS_SET}
    Log  %{THIS ENV VAR IS SET}

Environment Variables Are Space Sensitive 2
    [Documentation]  FAIL Environment variable '%{ THIS_ENV_VAR_IS_SET }' not found. Did you mean:
    ...    ${SPACE * 4}\%{THIS_ENV_VAR_IS_SET}
    Log  %{ THIS_ENV_VAR_IS_SET }

Environment Variables Are Underscore Sensitive
    [Documentation]  FAIL Environment variable '%{TH_IS_ENVVAR_IS_SET}' not found. Did you mean:
    ...    ${SPACE * 4}\%{THIS_ENV_VAR_IS_SET}
    Log  %{TH_IS_ENVVAR_IS_SET}

Environment Variables In Variable Table
    Should Contain  ${SCALAR PATH}  ${:}
    Should Contain  @{LIST PATH}[0]  ${:}
    Should Be Equal  ${SCALAR PATH}  %{PATH}
    Should Be Equal  @{LIST PATH}[0]  %{PATH}

Environment Variables In Settings Table
    Should Contain  @{TEST_TAGS}[0]  ${:}
    Should Be Equal  @{TEST_TAGS}[0]  %{PATH}

Environment Variables In Test Metadata
    [Documentation]  %{THIS_ENV_VAR_IS_SET} in a test doc
    [Tags]  %{THIS_ENV_VAR_IS_SET}
    Should Be Equal  @{TEST_TAGS}[0]  Env var value

Environment Variables In User Keyword Metadata
    ${ret} =  UK With Environment Variables In Metadata
    Should Be Equal  ${ret}  Env var value

Escaping Environment Variables
    Should Be Equal  \%{THIS_IS_NOT_ENV_VAR}  %\{THIS_IS_NOT_ENV_VAR}

Empty Environment Variable
    [Documentation]    FAIL    Invalid variable name '%{}'.
    Log  %{}

*** Keywords ***
UK With Environment Variables In Metadata
    [Arguments]  ${mypath}=%{PATH}
    [Documentation]  %{THIS_ENV_VAR_IS_SET} in a uk doc
    Should Contain  ${mypath}  ${:}
    [Return]  %{THIS_ENV_VAR_IS_SET}
