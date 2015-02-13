*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/deprecated_os/env_vars.robot
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Case ***
Deprecated OperatingSystem Should Be Imported Automatically When Operating System Is Imported
    Check Syslog Contains    Imported library 'DeprecatedOperatingSystem' with arguments [ ]
