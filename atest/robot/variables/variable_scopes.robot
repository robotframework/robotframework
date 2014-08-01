*** Setting ***
Documentation     These tests are somewhat related to tests in variable_priorities.html
Suite Setup       Run Tests    \    variables${/}variable_scopes.html
Force Tags        pybot    jybot    regression
Resource          atest_resource.robot

*** Variable ***

*** Test Case ***
Variables Set In Test Case Are Seen By User Keywords
    Check Test Case    Variables Set In Test Case Are Seen By User Keywords

Variables Set In One Test Are Not Visible In Another
    Check Test Case    Variables Set In One Test Are Not Visible In Another

Variables Set In User Keyword Are Seen Only By Lower Level User Keywords
    Check Test Case    Variables Set In User Keyword Are Seen Only By Lower Level User Keywords

*** Keyword ***
