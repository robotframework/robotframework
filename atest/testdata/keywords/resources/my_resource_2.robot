*** Keywords ***
Keyword Only In Resource 2
    Log    Keyword in resource 2

Use local keyword that exists also in another resource 2
    Keyword In Both Resources

Keyword In Both Resources
    Log    Keyword in resource 2

Keyword In All Resources And Libraries
    Log    Keyword in resource 2

Keyword Everywhere
    Log    Keyword in resource 2

keyword In TC File Overrides Others
    Fail    This keyword should not be called
