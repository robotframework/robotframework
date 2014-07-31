*** Setting ***
Suite Setup       Run Tests    \    standard_libraries${/}deprecated_builtin${/}deprecated.html
Force Tags        regression    jybot    pybot
Resource          atest_resource.txt

*** Variable ***

*** Test Case ***
Deprecated BuiltIn Should Be Imported Automatically
    Check Syslog Contains    Imported library 'DeprecatedBuiltIn' with arguments [ ] (

*** Keyword ***
