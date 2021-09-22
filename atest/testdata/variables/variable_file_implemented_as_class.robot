*** Settings ***
Variables    PythonClass.py
Variables    DynamicPythonClass.py    hello    world
Variables    InvalidClass.py

*** Test Cases ***
Python Class
    Should Be Equal    ${PYTHON STRING}    hello
    Should Be Equal    ${PYTHON INTEGER}    ${42}
    Should Be True    ${PYTHON LIST} == ['a', 'b', 'c']

Methods in Python Class Do Not Create Variables
    Variable Should Not Exist    ${python_method}

Properties in Python Class
    Should Be Equal    ${PYTHON PROPERTY}    value

Dynamic Python Class
    Should Be Equal    ${DYNAMIC PYTHON STRING}    hello world
    Should Be True    @{DYNAMIC PYTHON LIST} == ['hello', 'world']
    Should Be True    ${DYNAMIC PYTHON LIST} == ['hello', 'world']
