*** Settings ***
Library          Process

*** Variables ***
${C0}            ${EMPTY}
@{L0}            @{EMPTY}
${C1}            hello
@{L1}            hello
${C2}            two args
@{L2}            two    args
${C3}            "one arg"
@{L3}            one arg
${C4}            'one arg again'
@{L4}            one arg again
${C5}            multiple "args passed this time" and 'it ought to work'
@{L5}            multiple    args passed this time     and    it ought to work
${C6}            ä äŋd "öther nön-äcïï" ŝtüff 'hërë wë hävë'
@{L6}            ä    äŋd    öther nön-äcïï     ŝtüff    hërë wë hävë
${C7}            \u1234 "\u2603 \U0001F4A9"
@{L7}            \u1234    \u2603 \U0001F4A9
${C8}            c:\\temp "c:\\program files"
@{L8}            c:\\temp    c:\\program files
${C9}            "" ''
@{L9}            ${EMPTY}    ${EMPTY}
${BASICS}        10

*** Test Cases ***
Command line to list basics
    [Template]    Command line to list should succeed
    :FOR    ${i}    IN RANGE    ${BASICS}
    \    ${C${i}}    @{L${i}}
    "justone"    justone

Command line to list with internal quotes
    [Template]    Command line to list should succeed
    "inter'nal quotes"               inter'nal quotes
    'can be "surrounded"'            can be "surrounded"
    "with ''other'' quotes" '"""'    with ''other'' quotes    """

Command line to list with unbalanced quotes
    [Template]    Command line to list should fail
    "oo
    "
    '
    "foo"bar"
    foo'bar

Command line to list with escaping
    [Template]    Command line to list should succeed
    c:\\temp                          c:temp                       escaping=True
    c:\\\\temp                        c:\\temp                     escaping=True
    "c:\\temp"                        c:\\temp                     escaping=True
    'c:\\temp'                        c:\\temp                     escaping=True
    C:\\\\Program\\ Files\\\\Blaah    C:\\Program Files\\Blaah     escaping=True
    "C:\\Program Files\\Blaah"        C:\\Program Files\\Blaah     escaping=True
    'C:\\Program Files\\Blaah'        C:\\Program Files\\Blaah     escaping=True
    "internal \\"quotes\\"\\""        internal "quotes""           escaping=True
    'internal \\"quotes\\"\\"'        internal \\"quotes\\"\\"     escaping=True
    'internal \\'quotes\\'\\''        internal 'quotes''           escaping=True
    "internal \\'quotes\\'\\'"        internal \\'quotes\\'\\'     escaping=True
    \\\\\\"                           \\"                          escaping=True
    \\\\\\\\\\"                       \\\\"                        escaping=True
    \\\\\\"\\\\                       \\"\\                        escaping=True
    "\\\\\\"\\\\"                     \\"\\                        escaping=True

List to commandline basics
    [Template]    List to command line should succeed
    :FOR    ${i}    IN RANGE    ${BASICS}
    \    ${C${i}.replace("'", '"')}    @{L${i}}

List to commandline with internal quotes
    [Template]    List to command line should succeed
    "internal \\"double' quotes"       internal "double' quotes
    "will be \\"'escaped'\\"" ' \\"    will be "'escaped'"    '    "

List to commandline with escaping
    [Template]    List to command line should succeed
    c:\\temp                          c:\\temp
    "C:\\Program Files\\Blaah"        C:\\Program Files\\Blaah
    \\\\\\"                           \\"
    \\\\\\\\\\"                       \\\\"

*** Keywords ***
Command line to list should succeed
    [Arguments]    ${input}    @{expected}    &{config}
    ${result} =    Command line to list    ${input}    &{config}
    Should be equal    ${result}    ${expected}

Command line to list should fail
    [Arguments]    ${input}    ${error}=No closing quotation
    Run keyword and expect error    ValueError: Parsing '${input}' failed: ${error}
    ...    Command line to list    ${input}

List to command line should succeed
    [Arguments]    ${expected}    @{input}
    ${result} =    List to command line    @{input}
    Should be equal    ${result}    ${expected}
