*** Test Cases ***
Import Library works
    Import library      ${CURDIR}/global_listenerlibrary.py
    Events should be    end kw BuiltIn.Import Library
        ...             start kw global_listenerlibrary.Events Should Be
