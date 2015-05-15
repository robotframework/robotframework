*** Settings ***
Library    multiple_listenerlibrary.py

*** Test Cases ***
Multiple library listeners gets events
    Events should be    start test Multiple library listeners gets events
        ...             start kw multiple_listenerlibrary.Events Should Be
