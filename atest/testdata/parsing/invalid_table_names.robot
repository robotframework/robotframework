*** Error ***
This table causes error and stuff inside it is ignored.

*** Settings ***
Documentation    Executing tests ought to work anyway.
Resource         invalid_tables_resource.robot

*** ***
This kind of tables caused bug
https://github.com/robotframework/robotframework/issues/793

*** Test Cases ***
Test in valid table
    [Documentation]   FAIL No keyword with name 'Kw in valid table in resource' found.
    Keyword in valid table
    Kw in valid table in resource

*one more table cause an error

***Keywords***
Keyword in valid table
    Log    Keyword in valid table
