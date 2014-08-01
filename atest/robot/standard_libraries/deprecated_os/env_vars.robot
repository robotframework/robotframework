*** Setting ***
Suite Setup       Run Tests    \    standard_libraries${/}deprecated_os${/}env_vars.html
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Variable ***

*** Test Case ***
Delete Environment Variable
    Check testcase    Delete Environment Variable

Environment Variable Is Set
    Check testcase    Environment Variable Is Set

Environment Variable Is Not Set
    Check testcase    Environment Variable Is Not Set
