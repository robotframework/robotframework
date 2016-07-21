*** Settings ***
Library           listenerlibrary.py
Suite Setup       Events should be    Start suite: Test Scope 2
                  ...                 Start kw: listenerlibrary.Events Should Be
Suite Teardown    Events should be    Start suite: Test Scope 2
                  ...                 Start kw: listenerlibrary.Events Should Be
                  ...                 End kw: listenerlibrary.Events Should Be
                  ...                 Start kw: listenerlibrary.Events Should Be

*** Test Cases ***
Test scope library gets events 2
    Events should be    Start test: ${TEST NAME}
    ...                 Start kw: listenerlibrary.Events Should Be

Test scope library gets no previous events 2
    Events should be    Start test: ${TEST NAME}
    ...                 Start kw: listenerlibrary.Events Should Be
