*** Test Case ***
External variable not resolved
    ${external variable}=    Set variable    xxx
    Keyword attempting external tag

Argument is resolved
    Keyword with tag argument    This is an argument

Part of tag as argument
    Keyword with tag to complete    very

*** Keywords ***
Keyword with tag argument
    [Tags]    ${this tag}
    [Arguments]    ${this tag}
    No Operation

Keyword attempting external tag
    [Tags]    ${external}
    No Operation

Keyword with tag to complete
    [Tags]    Customisable tag is ${tag} cool
    [Arguments]    ${tag}
    No Operation
