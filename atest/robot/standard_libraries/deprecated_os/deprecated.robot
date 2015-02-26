*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/deprecated_os/misc.robot
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Case ***
Deprecated OperatingSystem Should Be Imported Automatically When Operating System Is Imported
    Check Syslog Contains    Imported library 'DeprecatedOperatingSystem' with arguments [ ]

Keywords Are Deprecated
     Check Log Message    @{ERRORS}[0]
    ...    Keyword 'DeprecatedOperatingSystem.List Dir' is deprecated. Use 'OperatingSystem.List Directory' instead.
    ...    WARN
    Check Log Message    @{ERRORS}[-1]
    ...    Keyword 'DeprecatedOperatingSystem.Count Items In Dir' is deprecated. Use 'OperatingSystem.Count Items In Directory' instead.
    ...    WARN
