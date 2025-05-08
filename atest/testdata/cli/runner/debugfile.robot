*** Settings ***
Library           DebugFileLibrary.py

*** Test Cases ***
Debug file messages are not delayed when timeouts are active
    [Timeout]    10 seconds
    Log and validate message is in debug file    ${DEBUG_FILE}
