*** Settings ***
Library           RecursiveTypedDict.py
Resource          conversion.resource

*** Test Cases ***
Recursive TypedDict
    Recursive    {'value': 1, 'children': []}    {'value': 1, 'children': []}
    Recursive    {'value': '1', 'children': [{'value': '2', 'children': []}]}
    ...          {'value': 1, 'children': [{'value': 2, 'children': []}]}
    Recursive    ${{{'value': '1', 'children': [{'value': '2', 'children': [{'value': '3', 'children': []}]}]}}}
    ...          {'value': 1, 'children': [{'value': 2, 'children': [{'value': 3, 'children': []}]}]}

Mutually recursive TypedDicts
    Mutually recursive    {'value': '1', 'child': None}    {'value': 1, 'child': None}
    Mutually recursive    {'value': '1', 'child': {'value': '2', 'parent': {'value': '3', 'child': None}}}
    ...                   {'value': 1, 'child': {'value': 2, 'parent': {'value': 3, 'child': None}}}

Invalid recursive TypedDict
    VAR    ${error}
    ...    Item 'children' got value '[{'value': 'bad', 'children': []}]' (list) that cannot be converted to List[Recursive]:
    ...    Item '0' got value '{'value': 'bad', 'children': []}' (dictionary) that cannot be converted to Recursive:
    ...    Item 'value' got value 'bad' that cannot be converted to integer.
    Conversion Should Fail    Recursive    {'value': 1, 'children': [{'value': 'bad', 'children': []}]}
    ...    type=Recursive    error=${error}
