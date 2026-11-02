*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${LIBRARY}
Resource          libdoc_resource.robot

*** Variables ***
${LIBRARY}        ${DATADIR}/keywords/type_conversion/RecursiveTypedDict.py

*** Test Cases ***
Recursive TypedDict
    Keyword Name Should Be         1    Recursive
    Keyword Arguments Should Be    1    argument: Recursive    expected=None
    Typedoc links should be        1    0    Recursive
    TypedDict Items Should Be      Recursive    value    children

Mutually recursive TypedDicts
    Keyword Name Should Be         0    Mutually Recursive
    Keyword Arguments Should Be    0    argument: Parent    expected=None
    Typedoc links should be        0    0    Parent
    TypedDict Items Should Be      Parent    value    child

HTML output
    Run Libdoc And Parse Model From HTML    ${LIBRARY}
    Should Be Equal    ${MODEL}[keywords][1][args][0][type][typedoc]    Recursive

*** Keywords ***
TypedDict Items Should Be
    [Arguments]    ${name}    @{expected}
    ${items} =    Get Elements    ${LIBDOC}    typedocs/type[@type='TypedDict'][@name='${name}']/items/item
    ${keys} =    Evaluate    [item.get('key') for item in $items]
    Should Be Equal    ${keys}    ${expected}
