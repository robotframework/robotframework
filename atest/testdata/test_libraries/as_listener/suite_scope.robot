*** Settings ***
Library    suite_listenerlibrary.py

*** Test Cases ***
Suite scope library gets events
    Events should be    start suite Suite Scope
        ...             start test Suite scope library gets events
        ...             start kw suite_listenerlibrary.Events Should Be

New test gets previous suite scope events
    Events should be    start suite Suite Scope
            ...         start test Suite scope library gets events
            ...         start kw suite_listenerlibrary.Events Should Be
            ...         end kw suite_listenerlibrary.Events Should Be
            ...         end test Suite scope library gets events
            ...         start test New test gets previous suite scope events
            ...         start kw suite_listenerlibrary.Events Should Be

Listener methods in library are keywords
    end_test   foo   zap

Listener methods starting with underscore are not keywords
    [Documentation]         FAIL No keyword with name '_end_keyword' found.
    _end_keyword   bar  zap
