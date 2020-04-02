*** Settings ***
Library           listenerlibrary.py
Suite Setup       Events should be    Start suite: Test Scope
                  ...                 Start kw: listenerlibrary.Events Should Be
Suite Teardown    Events should be    Start suite: Test Scope
                  ...                 Start kw: listenerlibrary.Events Should Be
                  ...                 End kw: listenerlibrary.Events Should Be
                  ...                 Start kw: listenerlibrary.Events Should Be

*** Test Cases ***
Test scope library gets events
    Events should be    Start test: ${TEST NAME}
    ...                 Start kw: listenerlibrary.Events Should Be

Test scope library gets no previous events
    Events should be    Start test: ${TEST NAME}
    ...                 Start kw: listenerlibrary.Events Should Be

Listener methods in library are keywords
    End test    foo    zap
    Events should be    Start test: ${TEST NAME}
    ...                 Start kw: listenerlibrary.End Test
    ...                 End test: foo
    ...                 End kw: listenerlibrary.End Test
    ...                 Start kw: listenerlibrary.Events Should Be

Listener methods starting with underscore are not keywords
    [Documentation]    FAIL
    ...    No keyword with name 'End keyword' found. Did you mean:
    ...    ${SPACE*4}BuiltIn.Run Keyword
    End keyword    bar    zap
