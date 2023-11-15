*** Settings ***
Suite Setup        Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/ReturnType.py
Test Template      Return type should be
Resource           libdoc_resource.robot

*** Test Cases ***
No return
    0    None

None return
    1    None

Simple return
    2    {'name': 'int', 'typedoc': 'integer', 'nested': [], 'union': False}

Parameterized return
    3    {'name': 'List',
    ...   'typedoc': 'list',
    ...   'nested': [{'name': 'int', 'typedoc': 'integer', 'nested': [], 'union': False}],
    ...   'union': False}

Union return
    4    {'name': 'Union',
    ...   'typedoc': None,
    ...   'nested': [{'name': 'int', 'typedoc': 'integer', 'nested': [], 'union': False},
    ...              {'name': 'float', 'typedoc': 'float', 'nested': [], 'union': False}],
    ...   'union': True}

Stringified return
    5    {'name': 'Union',
    ...   'typedoc': None,
    ...   'nested': [{'name': 'int', 'typedoc': 'integer', 'nested': [], 'union': False},
    ...              {'name': 'float', 'typedoc': 'float', 'nested': [], 'union': False}],
    ...   'union': True}

Unknown return
    6   {'name': 'Unknown', 'typedoc': None, 'nested': [], 'union': False}

Return types are in typedocs
    [Template]    Should Be Equal
    ${MODEL}[typedocs][0][name]         float
    ${MODEL}[typedocs][0][usages][0]    E Union Return
    ${MODEL}[typedocs][0][usages][1]    F Stringified Return
    ${MODEL}[typedocs][1][name]         integer
    ${MODEL}[typedocs][1][usages][0]    C Simple Return
    ${MODEL}[typedocs][1][usages][1]    D Parameterized Return
    ${MODEL}[typedocs][1][usages][2]    E Union Return
    ${MODEL}[typedocs][1][usages][3]    F Stringified Return
    ${MODEL}[typedocs][2][name]         list
    ${MODEL}[typedocs][2][usages][0]    D Parameterized Return

*** Keywords ***
Return type should be
    [Arguments]    ${index}    @{expected}
    VAR    ${expected}    @{expected}
    Should Be Equal As Strings
    ...    ${MODEL}[keywords][${index}][returnType]
    ...    ${expected}
