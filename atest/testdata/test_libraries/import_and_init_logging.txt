*** Settings ***
Library  ImportLogging.py
Library  InitLogging.py
Library  ConstructorLogging.java

*** Test Cases ***
No import/init time messages here
    ImportLogging.Keyword
    InitLogging.Keyword

No import/init time messages in Java either
    ConstructorLogging.Keyword
