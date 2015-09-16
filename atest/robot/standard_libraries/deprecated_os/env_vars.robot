*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/deprecated_os/env_vars.robot
Resource          atest_resource.robot

*** Test Case ***
Delete Environment Variable
    Check testcase    Delete Environment Variable

Environment Variable Is Set
    Check testcase    Environment Variable Is Set

Environment Variable Is Not Set
    Check testcase    Environment Variable Is Not Set
