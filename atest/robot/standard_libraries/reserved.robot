*** Setting ***
Documentation     Tests for keywords that are reserved for future use. Only some keywords are tested here because all have same dynamic implementation. All keywords that are currently reserved: ['for', 'while', 'break', 'continue', 'end', 'if', 'else', 'elif', 'else if', 'return']
Suite Setup       Run Tests    \    standard_libraries${/}reserved.html
Force Tags        regression    jybot    pybot
Resource          atest_resource.txt

*** Variable ***

*** Test Case ***
For
    Check testcase    For

Continue
    Check testcase    Continue

Reserved in User Keyword
    Check testcase    Reserved In User Keyword
