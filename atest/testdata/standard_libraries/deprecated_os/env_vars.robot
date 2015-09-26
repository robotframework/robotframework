*** Setting ***
Library           OperatingSystem

*** Variable ***
${NAME}           EXAMPLE_ENV_VAR_32FDHT

*** Test Case ***
Delete Environment Variable
    [Documentation]    FAIL Environment variable '${NAME}' does not exist.
    [Setup]    Set Environment Variable    ${NAME}    Hello
    Delete Environment Variable    ${NAME}
    Environment Variable Is Not Set    ${NAME}
    Delete Environment Variable    ${NAME}    # should not fail
    Get Environment Variable    ${NAME}

Environment Variable Is Set
    [Documentation]    FAIL Environment variable '${NAME}' is not set.
    [Setup]    Set Environment Variable    ${NAME}    Hello
    Environment Variable Is Set    ${NAME}
    Delete Environment Variable    ${NAME}
    Environment Variable Is Set    ${NAME}

Environment Variable Is Not Set
    [Documentation]    FAIL Environment variable '${NAME}' is set to 'Hello'.
    [Setup]    Delete Environment Variable    ${NAME}
    Environment Variable Is Not Set    ${NAME}
    Set Environment Variable    ${NAME}    Hello
    Environment Variable Is Not Set    ${NAME}
