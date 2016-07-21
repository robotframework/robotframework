*** Settings ***
Library           global_listenerlibrary.py
Suite Setup       Events should be    Start suite: Global Scope
                  ...                 Start kw: global_listenerlibrary.Events Should Be
Suite Teardown    Events should be    Start suite: Global Scope
                  ...                 Start kw: global_listenerlibrary.Events Should Be
                  ...                 End kw: global_listenerlibrary.Events Should Be
                  ...                 Start test: Global scope library gets events
                  ...                 Start kw: global_listenerlibrary.Events Should Be
                  ...                 End kw: global_listenerlibrary.Events Should Be
                  ...                 End test: Global scope library gets events
                  ...                 Start test: Global scope library gets all previous events
                  ...                 Start kw: global_listenerlibrary.Events Should Be
                  ...                 End kw: global_listenerlibrary.Events Should Be
                  ...                 End test: Global scope library gets all previous events
                  ...                 Start kw: global_listenerlibrary.Events Should Be

*** Test Cases ***
Global scope library gets events
    Events should be    Start suite: Global Scope
    ...                 Start kw: global_listenerlibrary.Events Should Be
    ...                 End kw: global_listenerlibrary.Events Should Be
    ...                 Start test: ${TEST NAME}
    ...                 Start kw: global_listenerlibrary.Events Should Be

Global scope library gets all previous events
    Events should be    Start suite: Global Scope
    ...                 Start kw: global_listenerlibrary.Events Should Be
    ...                 End kw: global_listenerlibrary.Events Should Be
    ...                 Start test: ${PREV TEST NAME}
    ...                 Start kw: global_listenerlibrary.Events Should Be
    ...                 End kw: global_listenerlibrary.Events Should Be
    ...                 End test: ${PREV TEST NAME}
    ...                 Start test: ${TEST NAME}
    ...                 Start kw: global_listenerlibrary.Events Should Be
