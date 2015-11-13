*** Settings ***
Library    multiple_listenerlibrary.py    WITH NAME    lib_works
Library    multiple_listenerlibrary.py    fail=Yes    WITH NAME    lib_not_works

*** Test Cases ***
Multiple library listeners gets events
    lib_works.Events should be    start test Multiple library listeners gets events
    ...                           start kw lib_works.Events Should Be
All listeners are disabled if one fails
    lib_not_works.Events should be empty

