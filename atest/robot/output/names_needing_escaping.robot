*** Settings ***
Documentation   Test case and user keyword names needing escaping because they contain
...    1) special characters in HTML (", <, ...)
...    2) special characters in Robot test data.
...    In latter case special chars actually aren't that special because they aren't escaped.
Suite Setup     Run Tests  ${EMPTY}  output/names_needing_escaping.robot
Resource        atest_resource.robot
Test Template   Check TC And UK Name

*** Test Cases ***
Quotes
    "Quotes"

Tag
    Tag <pre>

And
    And &

Backslashes
    Backslashes \\ \\\\ \\\\\\ \\\\\\\\

Variable
    Variable \${var}

Escaped variable
    Escaped \\\${var}

Newline And Tab
    Newline \\n and Tab \\t

*** Keywords ***
Check TC And UK Name
    [Arguments]  ${name}
    ${tc} =  Check Test Case  ${name}
    Should Be Equal  ${tc.name}  ${name}
    Should Be Equal  ${tc.kws[0].name}  ${name}
