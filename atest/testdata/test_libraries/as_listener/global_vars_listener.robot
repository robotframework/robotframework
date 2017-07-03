*** Settings ***
Documentation     Test global variables in 'close' listener method
Library           global_vars_listenerlibrary.py

*** Test Cases ***
Global variables test
    Log  NothingToDo

Global variables final test
    Log  NothingToDo
