*** Settings ***
Library           ListenerOrder.py    LIB 1       ${0}     AS    LIB 1
Library           ListenerOrder.py    LIB 2                AS    LIB 2
Library           ListenerOrder.py    NOT USED    bad      AS    BAD
Library           ListenerOrder.py    LIB 3       999.9    AS    LIB 3

*** Test Cases ***
Test
    Log    Hello, listeners!
