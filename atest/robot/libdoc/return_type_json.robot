*** Settings ***
Suite Setup        Run Libdoc And Parse Model From JSON    ${TESTDATADIR}/ReturnType.py
Test Template      Return type should be
Resource           libdoc_resource.robot
Test Tags          require-jsonschema

*** Test Cases ***
No return
    0    None

Never and NoReturn
    7    None
    8    None

None return
    1    {'name': 'None', 'typedoc': 'None', 'nested': [], 'union': False, 'alias': None}

Simple return
    2    {'name': 'int', 'typedoc': 'integer', 'nested': [], 'union': False, 'alias': None}

Parameterized return
    3    {'name': 'List',
    ...   'typedoc': 'list',
    ...   'nested': [{'name': 'int', 'typedoc': 'integer', 'nested': [], 'union': False, 'alias': None}],
    ...   'union': False, 'alias': None}

Union return
    4    {'name': 'Union',
    ...   'typedoc': None,
    ...   'nested': [{'name': 'int', 'typedoc': 'integer', 'nested': [], 'union': False, 'alias': None},
    ...              {'name': 'float', 'typedoc': 'float', 'nested': [], 'union': False, 'alias': None}],
    ...   'union': True, 'alias': None}

Stringified return
    5    {'name': 'Union',
    ...   'typedoc': None,
    ...   'nested': [{'name': 'int', 'typedoc': 'integer', 'nested': [], 'union': False, 'alias': None},
    ...              {'name': 'float', 'typedoc': 'float', 'nested': [], 'union': False, 'alias': None}],
    ...   'union': True, 'alias': None}

Type alias
    [Tags]    require-py3.12
    9   {'name': 'int', 'typedoc': 'integer', 'nested': [], 'union': False, 'alias': 'TypeAlias'}

Unknown return
    6   {'name': 'Unknown', 'typedoc': None, 'nested': [], 'union': False, 'alias': None}

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
    ${MODEL}[typedocs][1][usages][4]    K Type Alias
    ${MODEL}[typedocs][2][name]         list
    ${MODEL}[typedocs][2][usages][0]    D Parameterized Return

*** Keywords ***
Return type should be
    [Arguments]    ${index}    @{expected}
    VAR    ${expected}    @{expected}
    Should Be Equal As Strings
    ...    ${MODEL}[keywords][${index}][returnType]
    ...    ${expected}
