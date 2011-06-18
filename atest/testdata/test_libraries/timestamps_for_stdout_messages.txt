*** Settings ***
Library  PythonLibUsingTimestamps.py
Library  JavaLibUsingTimestamps.java


*** Test Cases ***

Library adds timestamp as integer
    Timestamp as integer

Library adds timestamp as float
    Timestamp as float

Java library adds timestamp
    Java timestamp
