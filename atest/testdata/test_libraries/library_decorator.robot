*** Settings ***
Library  LibraryDecorator.py

*** Test Cases ***
Set Library Version And Scope Using Library Decorator
    Library Decorator Disables Public Methods

Library Decorator Disables Public Methods
    [Documentation]  FAIL  No keyword with name 'Library Decorator Disables Public Methods' found.
    Library Decorator Disables Public Methods

Library Decorator Does Not Disable Decorated Public Methods
    Decorated Method Is Keyword
