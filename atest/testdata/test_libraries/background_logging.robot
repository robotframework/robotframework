*** Settings ***
Library    background_logs.py

*** Test Cases ***
Log main
    Log from main    Foo
Log from Background
    Log from background   Bar
    Log background messages
Log from specific thread
    Log from background   Ignored    threadA
    Log from background   Ignored    threadB
    Log from background   Huu        threadC
    Log from background   Ignored    threadD
    Log background messages     threadC
