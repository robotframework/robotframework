*** Test Cases ***
Import Library works
    Import library      listenerlibrary
    Events should be    End kw: BuiltIn.Import Library
    ...                 Start kw: listenerlibrary.Events Should Be
    Import library      ${CURDIR}/global_listenerlibrary.py
    listenerlibrary.Events should be
    ...                 End kw: BuiltIn.Import Library
    ...                 Start kw: listenerlibrary.Events Should Be
    ...                 End kw: listenerlibrary.Events Should Be
    ...                 Start kw: BuiltIn.Import Library
    ...                 End kw: BuiltIn.Import Library
    ...                 Start kw: listenerlibrary.Events Should Be
    global_listenerlibrary.Events should be
    ...                 End kw: BuiltIn.Import Library
    ...                 Start kw: listenerlibrary.Events Should Be
    ...                 End kw: listenerlibrary.Events Should Be
    ...                 Start kw: global_listenerlibrary.Events Should Be

Reload Library works
    Reload library      global_listenerlibrary
    global_listenerlibrary.Events should be
    ...                 End kw: BuiltIn.Import Library
    ...                 Start kw: listenerlibrary.Events Should Be
    ...                 End kw: listenerlibrary.Events Should Be
    ...                 Start kw: global_listenerlibrary.Events Should Be
    ...                 End kw: global_listenerlibrary.Events Should Be
    ...                 End test: ${PREV TEST NAME}
    ...                 Start test: ${TEST NAME}
    ...                 Start kw: BuiltIn.Reload Library
    ...                 End kw: BuiltIn.Reload Library
    ...                 Start kw: global_listenerlibrary.Events Should Be
    Reload library      listenerlibrary
    listenerlibrary.Events should be
    ...                 Start test: ${TEST NAME}
    ...                 Start kw: BuiltIn.Reload Library
    ...                 End kw: BuiltIn.Reload Library
    ...                 Start kw: global_listenerlibrary.Events Should Be
    ...                 End kw: global_listenerlibrary.Events Should Be
    ...                 Start kw: BuiltIn.Reload Library
    ...                 End kw: BuiltIn.Reload Library
    ...                 Start kw: listenerlibrary.Events Should Be
