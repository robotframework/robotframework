*** Keywords ***
Keyword Only In Resource 1
    Log    Keyword in resource 1

Use local keyword that exists also in another resource 1
    Keyword In Both Resources

Keyword In Both Resources
    Log    Keyword in resource 1

Keyword In All Resources And Libraries
    Log    Keyword in resource 1

Keyword In Resource 1 And Libraries
    Log    Keyword in resource 1

Use test case file keyword even when local keyword with same name exists
    Keyword Everywhere

Keyword Everywhere
    Log    Keyword in resource 1

keyword In TC File Overrides Others
    Fail    This keyword should not be called

Keyword In Resource Overrides Libraries
    Log    Keyword in resource 1

Using Test Case File User Keywords In Resource
    Using TestCase file UserKeywords

Using Resource File User Keywords In Resource 1
    Keyword ONLY in Resource _1_
    my_resource_1.keyword only in resource 1
    MY_ RESOURCE_ 1 . keywordonlyinresource1

Using Resource File User Keywords In Resource 2
    Keyword ONLY in Resource _2_
    my_resource_2.keyword only in resource 2
    MY_ RESOURCE_ 2 . keywordonlyinresource2

Using Base Keywords In Resource
    Keyword only in library 1
    mylibrary1.keyword ONLY IN library1
    M Y L I B R A R Y 1 . keywordonlyinlibrary1

Overrided in test case file with full name
    Log    Keyword in resource 1
