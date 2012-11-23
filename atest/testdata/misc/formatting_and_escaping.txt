*** Settings ***
Documentation
...  We have _formatting_ and <escaping>.
...
...  | *Name* | *URL* |
...  | Robot  | http://robotframework.org |
...  | Custom | [http://robotframework.org|link] |
Metadata    Escape   this is <b>not bold</b>
Metadata    Format   this is *bold*

*** Test Cases ***
Formatting
    [Documentation]    *I* can haz _formatting_ & <escaping>!!
    ...    - list
    ...    - here
    No Operation

<Escaping>
    [Tags]    *not bold*    <b>not bold either</b>
    <blink>NO</blink>    <&>


*** Keywords ***
<blink>NO</blink>
    [Arguments]    ${arg}
    Log    ${arg}
