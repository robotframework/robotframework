*** Settings ***
Library  LibraryDecorator.py
Library  LibraryDecoratorWithArgs.py

*** Test Cases ***
Set Library Version And Scope Using Library Decorator
    Library Decorator With Args Disables Public Methods

Library Decorator With Args Disables Public Methods
    [Documentation]  FAIL  No keyword with name 'Library Decorator With Args Disables Public Methods' found.
    Library Decorator With Args Disables Public Methods

Library Decorator With Args Does Not Disable Decorated Public Methods
    Decorated Method Is Keyword

Public Method From Library Decorator Is Not Recognized As Keyword
    [Documentation]  FAIL  No keyword with name 'Library Decorator Disables Public Methods' found.
    Library Decorator Disables Public Methods

Decorated Method From Libary Decorator Is Recognized As Keyword
    Method From Library Decorator
