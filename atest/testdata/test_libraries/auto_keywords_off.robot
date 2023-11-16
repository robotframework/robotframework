*** Settings ***
Library               ClassWithAutoKeywordsOff.py
Library               ModuleWithAutoKeywordsOff.py

*** Test Cases ***
Public Method Is Not Recognized As Keyword
    [Documentation]  FAIL  No keyword with name 'Public Method Is Not Keyword' found.
    Public Method Is Not Keyword

Decorated Method Is Recognized As Keyword
    Decorated Method Is Keyword
    Decorated Method In Module Is Keyword

Private Method Is Not Recognized As Keyword
    [Documentation]  FAIL  No keyword with name 'Private Method Is Not Keyword' found.
    Private Method Is Not Keyword

Private Decorated Method Is Recognized As Keyword
    Private Decorated Method Is Keyword
    Private Decorated Method In Module Is Keyword

Invalid __getattr__ is handled
    [Documentation]  FAIL  No keyword with name 'Invalid Getattr' found.
    Invalid Getattr
