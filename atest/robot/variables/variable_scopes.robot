*** Setting ***
Documentation     These tests are somewhat related to tests in variable_priorities.robot
Suite Setup       Run Tests    ${EMPTY}    variables/variable_scopes.robot
Force Tags        pybot    jybot    regression
Resource          atest_resource.robot

*** Test Case ***
Variables Set In Test Case Are Seen By User Keywords
    Check Test Case    Variables Set In Test Case Are Seen By User Keywords

Variables Set In One Test Are Not Visible In Another
    Check Test Case    Variables Set In One Test Are Not Visible In Another

Variables Set In User Keyword Are Seen Only By Lower Level User Keywords
    Check Test Case    Variables Set In User Keyword Are Seen Only By Lower Level User Keywords
