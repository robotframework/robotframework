*** Setting ***
Suite Setup       Run Tests    \    standard_libraries${/}deprecated_os${/}deprecated.html
Force Tags        regression    jybot    pybot
Resource          atest_resource.txt

*** Variable ***

*** Test Case ***
Deprecated OperatingSystem Should Be Imported Automatically When Operating System Is Imported
    Check Syslog Contains    Imported library 'DeprecatedOperatingSystem' with arguments [ ]

*** Keyword ***
