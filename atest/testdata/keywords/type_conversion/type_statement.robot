*** Settings ***
Test Tags       require-py3.12
Library         TypeStatement.py
Resource        conversion.resource

*** Test Cases ***
Simple value
    Simple value           1                1

Params in value
    Params value           []               []
    Params value           [1, "2", 3.0]    [1, 2, 3]

Union value
    Union value            1                1
    Union value            1.2              1.2

Enum value
    Enum value             ON               ON
    Enum value             off              OFF

Typed dict value
    Typed dict value       {"x": 1, "y": 0}    {"x": 1, "y": 0}

Forward reference
    Forward Ref            1                1

Recursion
    Recursive              1                1
    Recursive              [1, 2, 3]        [1, 2, 3]
    Recursive              [1.0, "2", 3]    [1, 2, 3]
    Recursive              [[[1, "2"]]]     [[[1, 2]]]
    Recursive              [[[[[[0]]]]]]    [[[[[[0]]]]]]

Failing recursive conversion
    [Template]             Conversion Should Fail
    Recursive              bad              type=integer or list[Recursive]
    Recursive              [1, 2.3]         type=integer or list[Recursive]

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
    Generic Forward Ref    [1]              [1]
    Generic Forward Ref    [1.0, 2, "3"]    [1, 2, 3]

Alias as generic parameter
    Alias as param         []               []
    Alias as param         [1]              [1]
    Alias as param         [1.0, 2, "3"]    [1, 2, 3]

Alias in union
    Alias in union         1                1
    Alias in union         []               []
    Alias in union         [1]              [1]
    Alias in union         [1.0, 2, "3"]    [1, 2, 3]
