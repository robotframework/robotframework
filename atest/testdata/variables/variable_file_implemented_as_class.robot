*** Settings ***
Variables    PythonClass.py
Variables    DynamicPythonClass.py    hello    world
Variables    JavaClass.java
Variables    DynamicJavaClass.class    hi    tellus
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

Java Class
    Should Be Equal    ${JAVA STRING}    hi
    Should Be Equal    ${JAVA INTEGER}    ${-1}
    Should Be True    @{JAVA LIST} == ['x', 'y', 'z']

Methods in Java Class Do Not Create Variables
    Variable Should Not Exist    ${javaMethod}
    Variable Should Not Exist    ${equals}
    Variable Should Not Exist    ${toString}
    Variable Should Not Exist    ${class}

Properties in Java Class
    Should Be Equal    ${JAVA PROPERTY}    default

Dynamic Java Class
    Should Be Equal    ${DYNAMIC JAVA STRING}    hi tellus
    Should Be True    @{DYNAMIC JAVA LIST} == ['hi', 'tellus']
