*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/deprecated_builtin/deprecated.robot
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Case ***
Deprecated BuiltIn Should Be Imported Automatically
    Check Syslog Contains    Imported library 'DeprecatedBuiltIn' with arguments [ ] (
