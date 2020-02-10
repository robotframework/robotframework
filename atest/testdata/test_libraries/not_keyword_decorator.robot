*** Settings ***
Library           ModuleWitNotKeywordDecorator.py
Library           ClassWithNotKeywordDecorator.py
Library           HybridWithNotKeywordDecorator.py

*** Test Cases ***
In module
    [Documentation]    FAIL    STARTS: No keyword with name 'Not exposed in module' found. Did you mean:
    Exposed in module
    Not exposed in module

Hide imported function
    [Documentation]    FAIL    No keyword with name 'Abspath' found.
    Abspath

Set 'robot_not_keyword' attribute directly
    [Documentation]    FAIL    No keyword with name 'Not exposed by setting attribute' found.
    Not exposed by setting attribute

Even '@keyword' cannot disable '@not_keyword'
    [Documentation]    FAIL    No keyword with name 'Keyword and not keyword' found.
    Keyword and not keyword

'@not_keyword' is not exposed
    [Documentation]    FAIL    STARTS: No keyword with name 'Not keyword' found. Did you mean:
    Not keyword

'@keyword' is not exposed
    [Documentation]    FAIL    STARTS: No keyword with name 'Keyword' found. Did you mean:
    Keyword

'@library' is not exposed
    [Documentation]    FAIL    No keyword with name 'Library' found.
    Library

In class
    [Documentation]    FAIL    STARTS: No keyword with name 'Not exposed in class' found. Did you mean:
    Exposed in class
    Not exposed in class

In hybrid library
    [Documentation]    FAIL    STARTS: No keyword with name 'Not exposed in hybrid' found. Did you mean:
    Exposed in hybrid
    Not exposed in hybrid
