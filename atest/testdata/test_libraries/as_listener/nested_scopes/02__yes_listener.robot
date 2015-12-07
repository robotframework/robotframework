*** Settings ***
Library           ../listenerlibrary.py    WITH NAME    test
Library           ../suite_listenerlibrary.py    WITH NAME    suite
Library           ../global_listenerlibrary.py    WITH NAME    global
Suite Setup       Suite Setup
Suite Teardown    Suite Teardown

*** Test Cases ***
Yes listener
    test.Events should be      Start test: Yes listener
    ...                        Start kw: test.Events Should Be
    suite.Events should be     Start suite: Yes Listener
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End kw: Suite Setup
    ...                        Start test: Yes listener
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    global.Events should be    Start suite: Nested Scopes
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End kw: Suite Setup
    ...                        Start suite: Yes Listener
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End kw: Suite Setup
    ...                        Start test: Yes listener
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be

*** Keywords ***
Suite Setup
    test.Events should be      Start suite: Yes Listener
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    suite.Events should be     Start suite: Yes Listener
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    global.Events should be    Start suite: Nested Scopes
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End kw: Suite Setup
    ...                        Start suite: Yes Listener
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be

Suite Teardown
    test.Events should be      Start suite: Yes Listener
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End kw: Suite Setup
    ...                        Start kw: Suite Teardown
    ...                        Start kw: test.Events Should Be
    suite.Events should be     Start suite: Yes Listener
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End kw: Suite Setup
    ...                        Start test: Yes listener
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End test: Yes listener
    ...                        Start kw: Suite Teardown
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    global.Events should be    Start suite: Nested Scopes
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End kw: Suite Setup
    ...                        Start suite: Yes Listener
    ...                        Start kw: Suite Setup
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End kw: Suite Setup
    ...                        Start test: Yes listener
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
    ...                        End kw: global.Events Should Be
    ...                        End test: Yes listener
    ...                        Start kw: Suite Teardown
    ...                        Start kw: test.Events Should Be
    ...                        End kw: test.Events Should Be
    ...                        Start kw: suite.Events Should Be
    ...                        End kw: suite.Events Should Be
    ...                        Start kw: global.Events Should Be
