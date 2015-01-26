*** Settings ***
Library  ImportLogging.py
Library  InitLogging.py
Library  ConstructorLogging.java
Library  InitImportingAndIniting.Importing
Library  InitImportingAndIniting.Initted    id=42
Library  InitImportingAndIniting.Initting

*** Test Cases ***
No import/init time messages here
    ImportLogging.Keyword
    InitLogging.Keyword

No import/init time messages in Java either
    ConstructorLogging.Keyword

Importing and initializing libraries in init
    Kw from lib with importing init
    Convert to lower case    Using kw from lib imported by init
    Kw from lib with initting init
    Kw from lib initted by init
