*** Settings ***
Library         BinaryDataLibrary

*** Test Cases ***
Print Bytes
    Print Bytes

Byte Error
    [Documentation]  FAIL  REGEXP: Bytes 0, 10, 127, 255: .*
    Raise Byte Error

Byte Error In Setup And Teardown
    [Documentation]  FAIL  REGEXP: Setup failed:\nBytes 0, 10, 127, 255: .*\n\nAlso teardown failed:\nBytes 0, 10, 127, 255: .*
    [Setup]  Raise Byte Error
    No Operation
    [Teardown]  Raise Byte Error

Binary Data
    Print Binary Data

