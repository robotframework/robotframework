*** Settings ***
Library    global_listenerlibrary.py

*** Test Cases ***
Global scope library gets events
    Events should be    start suite Global Scope
        ...             start test Global scope library gets events
        ...             start kw global_listenerlibrary.Events Should Be

New test gets previous global scope events
    Events should be    start suite Global Scope
            ...         start test Global scope library gets events
            ...         start kw global_listenerlibrary.Events Should Be
            ...         end kw global_listenerlibrary.Events Should Be
            ...         end test Global scope library gets events
            ...         start test New test gets previous global scope events
            ...         start kw global_listenerlibrary.Events Should Be
