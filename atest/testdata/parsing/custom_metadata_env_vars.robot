*** Settings ***
Documentation     Test data for environment variables in custom metadata.

*** Test Cases ***
Environment Variables Test
    [Documentation]    Test custom metadata with environment variables
    [Environment]     %{CUSTOM_ENV_VAR}
    [System Path]     %{PATH=default_path}
    [Home Dir]        %{HOME=%{USERPROFILE=C:\\Users\\Default}}
    Log    Environment variables test
