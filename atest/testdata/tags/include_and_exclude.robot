*** Settings ***
Force Tags      force    robot:just-an-example    ROBOT : XXX

*** Test Cases ***
Incl-1
    [Tags]  incl1
    No Operation

Incl-12
    [Tags]  incl 1  incl 2
    No Operation

Incl-123
    [Tags]  incl_1  incl_2  incl_3
    No Operation

excl-1
    [Tags]  excl1
    No Operation

Excl-12
    [Tags]  excl 1  excl 2
    No Operation

Excl-123
    [Tags]  excl_1  excl_2  excl_3
    No Operation

Robot-exclude
    [Tags]  robot:exclude  ROBOT:EXCLUDE
    Fail  This test will never be run
