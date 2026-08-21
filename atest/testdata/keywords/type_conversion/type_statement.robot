*** Settings ***
Library         TypeStatement.py
Test Tags       require-py3.12

*** Test Cases ***
Simple value
    Simple value           1                1

Params in value
    Params value           []               []
    Params value           [1, "2", 3.0]    [1, 2, 3]

Union value
    Union value            1                1
    Union value            1.2              1.2

Forward reference
    Forward Ref            1                1

Generic simple
    Generic Simple         1                1

Generic with params in value
    Generic Params         []               []
    Generic Params         [1, 2.0, "3"]    [1, 2, 3]

Generic with union
    Generic Union          1                1
    Generic Union          1.2              1.2

Generic with defaults
    [Tags]    require-py3.13
    Generic defaults 1     42               42
    Generic defaults 1     None             None
    Generic defaults 2     42               42
    Generic defaults 2     4.2              4.2

Generic forward reference
    Generic Forward Ref    []               []
    Generic Forward Ref    [1.0, 2, "3"]    [1, 2, 3]
