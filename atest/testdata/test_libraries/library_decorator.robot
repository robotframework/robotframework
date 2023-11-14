*** Settings ***
Library           LibraryDecorator.py
Library           LibraryDecoratorWithArgs.py
Library           LibraryDecoratorWithAutoKeywords.py

*** Test Cases ***
Library decorator disables automatic keyword discovery
    [Documentation]    FAIL STARTS: No keyword with name 'Not keyword' found. Did you mean:
    Decorated method is keyword
    Not keyword

Static and class methods when automatic keyword discovery is disabled
    Decorated static method is keyword
    Decorated class method is keyword

Library decorator with arguments disables automatic keyword discovery by default
    [Documentation]    FAIL No keyword with name 'Not keyword v2' found.
    Decorated method is keyword v.2
    Not keyword v2

Library decorator can enable automatic keyword discovery
    Undecorated method is keyword
    Decorated method is keyword as well
