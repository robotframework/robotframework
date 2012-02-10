*** Settings ***
Documentation   %{PATH} used in suite documentation
Suite Setup     Set Environment Variable  THIS_ENV_VAR_IS_SET  Env var value
Default Tags    %{PATH}
Meta: PATH      %{PATH}
Library         OperatingSystem

*** Variables ***
${PATH}  %{PATH}
@{PATH}  %{PATH}

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

Leading And Trailing Spaces Are Ignored Environment Variable Name
    Should Be Equal  %{ THIS_ENV_VAR_IS_SET }  Env var value

Non-Existing Environment Variable
    [Documentation]  FAIL Environment variable 'NON_EXISTING' does not exist
    Log  %{NON_EXISTING}

Environment Variables Are Case Sensitive
    [Documentation]  FAIL Environment variable 'this_env_var_is_set' does not exist
    Log  %{this_env_var_is_set}

Environment Variables Are Not Case Sensitive On Windows
    [Documentation]  On Windows case is not sensitive.
    Log  %{this_env_var_is_set}

Environment Variables Are Space Sensitive
    [Documentation]  FAIL Environment variable 'THIS ENV VAR IS SET' does not exist
    Log  %{THIS ENV VAR IS SET}

Environment Variables Are Underscore Sensitive
    [Documentation]  FAIL Environment variable 'TH_IS_ENVVAR_IS_SET' does not exist
    Log  %{TH_IS_ENVVAR_IS_SET}

Environment Variables In Variable Table
    Should Contain  ${PATH}  ${:}
    Should Contain  @{PATH}[0]  ${:}
    Should Be Equal  ${PATH}  %{PATH}
    Should Be Equal  @{PATH}[0]  %{PATH}

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

Empty Environment Variable Is No Recognized
    Should Be Equal  %{}  \%{}
    Should Be Equal  %{ }  \%{ }

*** Keywords ***
UK With Environment Variables In Metadata
    [Arguments]  ${mypath}=%{PATH}
    [Documentation]  %{THIS_ENV_VAR_IS_SET} in a uk doc
    Should Contain  ${mypath}  ${:}
    [Return]  %{THIS_ENV_VAR_IS_SET}

