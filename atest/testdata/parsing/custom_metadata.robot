*** Settings ***
Metadata    Version    1.0
Metadata    Author     Development Team    QA Team    Bettina
Metadata    System     ${{platform.version()}}
Metadata    What happens to a very long key?    Value here
Metadata    Multiline    Mein erwartetes Ergebnis
...
...    ist hier
...     auf mehrerene Lines

*** Test Cases ***
Login Test
    [Owner]           John Doe    Zweiter Wert
    [Requirement]     ACC-123
    [Priority]        High
    [Component]       Authentication
    [My Custom Metadata]    My Custom Metadata
    [Empty Metadata]
    [System]    ${{platform.version()}}
    [Tags]    abc    def
    [Multiline]    Multiline    Mein erwartetes Ergebnis
    ...
    ...    ist hier
    ...     auf mehrerene Lines    
    Login With Valid Credentials


*** Keywords ***
Login With Valid Credentials
    [Documentation]    Multiline
    ...    Documentation
    ...    blabla
    [Owner]         Jane Doe    
    [API]           https://api.example.com/login
    [Complexity]    Medium
    [My Requirement]    ACC-567
    No Operation
