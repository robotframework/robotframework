*** Settings ***
Library                       robot_keyword_Annotations.py

*** Keywords ***
List
    [Arguments]    ${argument: List}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

List With Params
    [Arguments]    ${argument: 'List[int]'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Sequence
    [Arguments]    ${argument: 'Sequence'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Sequence With Params
    [Arguments]    ${argument: 'Sequence[bool]'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mutable Sequence
    [Arguments]    ${argument: 'MutableSequence'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mutable Sequence With Params
    [Arguments]    ${argument: 'MutableSequence[bool]'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Dict
    [Arguments]    ${argument: 'Dict' }    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Dict With Params
    [Arguments]    ${argument: Dict[str, int] }    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mapping
    [Arguments]    ${argument:Mapping}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mapping With Params
    [Arguments]    ${argument: Mapping[bool, int]}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mutable Mapping
    [Arguments]    ${argument: 'MutableMapping'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mutable Mapping With Params
    [Arguments]    ${argument: MutableMapping[bool, int]}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Set
    [Arguments]    ${argument: 'Set'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Set With Params
    [Arguments]    ${argument: Set[bool]}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mutable Set
    [Arguments]    ${argument: 'MutableSet'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mutable Set With Params
    [Arguments]    ${argument: MutableSet[bool]}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

None As Default
    [Arguments]   ${argument:list}=${Empty}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Forward Reference
    [Arguments]   ${argument:'List'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Forward Ref With Params
    [Arguments]   ${argument:'List[int]'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}
