*** Settings ***
Test Tags         require-py3.12
Resource          libdoc_resource.robot

*** Variables ***
${LIBRARY}        ${DATADIR}/keywords/type_conversion/TypeStatement.py
${INXML}          ${OUTBASE}.in.xml
${INJSON}         ${OUTBASE}.in.json

*** Test Cases ***
Robot to XML
    [Documentation]    Also acts as setup to following two tests.
    Run Libdoc And Parse Output    ${LIBRARY}
    Validate XML Type Info
    Copy File    ${OUTXML}    ${INXML}

XML to XML
    [Setup]    File Should Exist    ${INXML}
    Run Libdoc And Parse Model From JSON    ${INXML}
    Validate JSON Type Info

XML to JSON
    [Setup]    File Should Exist    ${INXML}
    Run Libdoc And Parse Model From JSON    ${INXML}
    Validate JSON Type Info

Robot to JSON
    [Documentation]    Also acts as setup to following two tests.
    Run Libdoc And Parse Model From JSON    ${LIBRARY}
    Validate JSON Type Info
    Copy File    ${OUTJSON}    ${INJSON}

JSON to JSON
    [Setup]    File Should Exist    ${INJSON}
    Run Libdoc And Parse Model From JSON    ${INJSON}
    Validate XML Type Info

JSON to XML
    [Setup]    File Should Exist    ${INJSON}
    Run Libdoc And Parse Output    ${INJSON}
    Validate XML Type Info

*** Keywords ***
Validate XML Type Info
    [Documentation]
    ...    This keyword only tests alias names, not types they have been resolved to.
    ...    That is tested with JSON, though, and tests using XML input ensure that also XML is valid.
    ...
    ...    Negative indices are used because keywords using type alias defaults are not created
    ...    with Python 3.12. Finding keywords by name, not by index, would be better.
    Keyword Name Should Be           0    Alias As Param
    Keyword Arguments Should Be      0    argument: list[SimpleValue]                   expected: list[int]
    Keyword Name Should Be           1    Alias In Union
    Keyword Arguments Should Be      1    argument: SimpleValue | GenericParams[int]    expected: int | list[int]
    Keyword Name Should Be           2    Enum Value
    Keyword Arguments Should Be      2    argument: EnumValue                           expected: Toggle
    Keyword Name Should Be           3    Forward Ref
    Keyword Arguments Should Be      3    argument: ForwardRef                          expected: int
    Keyword Name Should Be          -9    Generic Forward Ref
    Keyword Arguments Should Be     -9    argument: GenericForwardRef[int]              expected: list[int]
    Keyword Name Should Be          -8    Generic Params
    Keyword Arguments Should Be     -8    argument: GenericParams[int]                  expected: list[int]
    Keyword Name Should Be          -7    Generic Simple
    Keyword Arguments Should Be     -7    argument: GenericSimple[int]                  expected: int
    Keyword Name Should Be          -6    Generic Union
    Keyword Arguments Should Be     -6    argument: GenericUnion[int, float]            expected: int | float
    Keyword Name Should Be          -5    Params Value
    Keyword Arguments Should Be     -5    argument: ParamsValue                         expected: list[int]
    Keyword Name Should Be          -4    Recursive
    Keyword Arguments Should Be     -4    argument: Recursive                           expected: int | list = -1
    Keyword Name Should Be          -3    Simple Value
    Keyword Arguments Should Be     -3    argument: SimpleValue                         expected: int
    Keyword Name Should Be          -2    Typed Dict Value
    Keyword Arguments Should Be     -2    argument: TypedDictValue                      expected: Point
    Keyword Name Should Be          -1    Union Value
    Keyword Arguments Should Be     -1    argument: UnionValue                          expected: int | float

Validate JSON Type Info
    [Documentation]
    ...    Tests alias names as well as types they are resolved to. Ugly but thorough.
    ...
    ...    Negative indices are used because keywords using type alias defaults are not created
    ...    with Python 3.12. Finding keywords by name, not by index, would be better.
    VAR    ${kws}    ${MODEL}[keywords]
    Should Be Equal    ${kws}[0][name]                                          Alias As Param
    Should Be Equal    ${kws}[0][args][0][type][name]                           list
    Should Be Equal    ${kws}[0][args][0][type][alias]                          ${None}
    Should Be Equal    ${kws}[0][args][0][type][nested][0][name]                int
    Should Be Equal    ${kws}[0][args][0][type][nested][0][alias]               SimpleValue
    Should Be Equal    ${kws}[1][name]                                          Alias In Union
    Should Be Equal    ${kws}[1][args][0][type][name]                           Union
    Should Be Equal    ${kws}[1][args][0][type][alias]                          ${None}
    Should Be Equal    ${kws}[1][args][0][type][nested][0][name]                int
    Should Be Equal    ${kws}[1][args][0][type][nested][0][alias]               SimpleValue
    Should Be Equal    ${kws}[1][args][0][type][nested][1][name]                list
    Should Be Equal    ${kws}[1][args][0][type][nested][1][alias]               GenericParams[int]
    Should Be Equal    ${kws}[1][args][0][type][nested][1][nested][0][name]     int
    Should Be Equal    ${kws}[1][args][0][type][nested][1][nested][0][alias]    ${None}
    Should Be Equal    ${kws}[2][name]                                          Enum Value
    Should Be Equal    ${kws}[2][args][0][type][name]                           Toggle
    Should Be Equal    ${kws}[2][args][0][type][alias]                          EnumValue
    Should Be Equal    ${kws}[3][name]                                          Forward Ref
    Should Be Equal    ${kws}[3][args][0][type][name]                           int
    Should Be Equal    ${kws}[3][args][0][type][alias]                          ForwardRef
    Should Be Equal    ${kws}[-9][name]                                         Generic Forward Ref
    Should Be Equal    ${kws}[-9][args][0][type][name]                          list
    Should Be Equal    ${kws}[-9][args][0][type][alias]                         GenericForwardRef[int]
    Should Be Equal    ${kws}[-9][args][0][type][nested][0][name]               int
    Should Be Equal    ${kws}[-9][args][0][type][nested][0][alias]              ${None}
    Should Be Equal    ${kws}[-8][name]                                         Generic Params
    Should Be Equal    ${kws}[-8][args][0][type][name]                          list
    Should Be Equal    ${kws}[-8][args][0][type][alias]                         GenericParams[int]
    Should Be Equal    ${kws}[-8][args][0][type][nested][0][name]               int
    Should Be Equal    ${kws}[-8][args][0][type][nested][0][alias]              ${None}
    Should Be Equal    ${kws}[-7][name]                                         Generic Simple
    Should Be Equal    ${kws}[-7][args][0][type][name]                          int
    Should Be Equal    ${kws}[-7][args][0][type][alias]                         GenericSimple[int]
    Should Be Empty    ${kws}[-7][args][0][type][nested]
    Should Be Equal    ${kws}[-6][name]                                         Generic Union
    Should Be Equal    ${kws}[-6][args][0][type][name]                          Union
    Should Be Equal    ${kws}[-6][args][0][type][alias]                         GenericUnion[int, float]
    Should Be Equal    ${kws}[-6][args][0][type][nested][0][name]               int
    Should Be Equal    ${kws}[-6][args][0][type][nested][0][alias]              ${None}
    Should Be Equal    ${kws}[-6][args][0][type][nested][1][name]               float
    Should Be Equal    ${kws}[-6][args][0][type][nested][1][alias]              ${None}
    Should Be Equal    ${kws}[-5][name]                                         Params Value
    Should Be Equal    ${kws}[-5][args][0][type][name]                          list
    Should Be Equal    ${kws}[-5][args][0][type][alias]                         ParamsValue
    Should Be Equal    ${kws}[-5][args][0][type][nested][0][name]               int
    Should Be Equal    ${kws}[-5][args][0][type][nested][0][alias]              ${None}
    Should Be Equal    ${kws}[-4][name]                                         Recursive
    Should Be Equal    ${kws}[-4][args][0][type][name]                          Union
    Should Be Equal    ${kws}[-4][args][0][type][alias]                         Recursive
    Should Be Equal    ${kws}[-4][args][0][type][nested][0][name]               int
    Should Be Equal    ${kws}[-4][args][0][type][nested][0][alias]              ${None}
    Should Be Equal    ${kws}[-4][args][0][type][nested][1][name]               list
    Should Be Equal    ${kws}[-4][args][0][type][nested][1][alias]              ${None}
    Should Be Equal    ${kws}[-4][args][0][type][nested][1][nested][0][name]    Recursive
    Should Be Equal    ${kws}[-4][args][0][type][nested][1][nested][0][alias]   ${None}
    Should Be Equal    ${kws}[-3][name]                                         Simple Value
    Should Be Equal    ${kws}[-3][args][0][type][name]                          int
    Should Be Equal    ${kws}[-3][args][0][type][alias]                         SimpleValue
    Should Be Equal    ${kws}[-2][name]                                         Typed Dict Value
    Should Be Equal    ${kws}[-2][args][0][type][name]                          Point
    Should Be Equal    ${kws}[-2][args][0][type][alias]                         TypedDictValue
    Should Be Equal    ${kws}[-1][name]                                         Union Value
    Should Be Equal    ${kws}[-1][args][0][type][name]                          Union
    Should Be Equal    ${kws}[-1][args][0][type][alias]                         UnionValue
    Should Be Equal    ${kws}[-1][args][0][type][nested][0][name]               int
    Should Be Equal    ${kws}[-1][args][0][type][nested][0][alias]              ${None}
    Should Be Equal    ${kws}[-1][args][0][type][nested][1][name]               float
    Should Be Equal    ${kws}[-1][args][0][type][nested][1][alias]              ${None}
