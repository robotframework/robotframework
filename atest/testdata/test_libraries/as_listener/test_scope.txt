*** Settings ***
Library    listenerlibrary.py
Suite setup     Events should be    start suite Test Scope
                ...                 start kw listenerlibrary.Events Should Be
Suite teardown  Events should be    start suite Test Scope
                ...                 start kw listenerlibrary.Events Should Be
                ...                 end kw listenerlibrary.Events Should Be
                ...                 start kw listenerlibrary.Events Should Be

*** Test Cases ***
Test scope library gets events
    Events should be    start test Test scope library gets events
        ...             start kw listenerlibrary.Events Should Be

New test gets empty events
    Events should be    start test New test gets empty events
        ...             start kw listenerlibrary.Events Should Be
