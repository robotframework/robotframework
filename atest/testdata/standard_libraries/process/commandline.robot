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
Split command line basics
    [Template]    Split command line should succeed
    FOR    ${i}    IN RANGE    ${BASICS}
        ${C${i}}    @{L${i}}
    END
    "justone"    justone

Split command line with internal quotes
    [Template]    Split command line should succeed
    "inter'nal quotes"               inter'nal quotes
    'can be "surrounded"'            can be "surrounded"
    "with ''other'' quotes" '"""'    with ''other'' quotes    """

Split command line with unbalanced quotes
    [Template]    Split command line should fail
    "oo
    "
    '
    "foo"bar"
    foo'bar

Split command line with escaping
    [Template]    Split command line should succeed
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

Split command line with pathlib.Path
    [Template]    Split command line should succeed
    ${{pathlib.Path($TEMPDIR)}}    ${TEMPDIR}

Join command line basics
    [Template]    Join command line should succeed
    FOR    ${i}    IN RANGE    ${BASICS}
        ${C${i}.replace("'", '"')}    @{L${i}}
    END

Join command line with internal quotes
    [Template]    Join command line should succeed
    "internal \\"double' quotes"       internal "double' quotes
    "will be \\"'escaped'\\"" ' \\"    will be "'escaped'"    '    "

Join command line with escaping
    [Template]    Join command line should succeed
    c:\\temp                          c:\\temp
    "C:\\Program Files\\Blaah"        C:\\Program Files\\Blaah
    \\\\\\"                           \\"
    \\\\\\\\\\"                       \\\\"

Join command line with non-strings
    [Template]    Join command line should succeed
    ${TEMPDIR}          ${{pathlib.Path($TEMPDIR)}}
    -n 42 ${TEMPDIR}    -n    ${42}    ${{pathlib.Path($TEMPDIR)}}

*** Keywords ***
Split command line should succeed
    [Arguments]    ${input}    @{expected}    &{config}
    ${result} =    Split command line    ${input}    &{config}
    Should be equal    ${result}    ${expected}

Split command line should fail
    [Arguments]    ${input}    ${error}=No closing quotation
    Run keyword and expect error
    ...    ValueError: Parsing '${input}' failed: ${error}
    ...    Split command line    ${input}

Join command line should succeed
    [Arguments]    ${expected}    @{input}
    ${result} =    Join command line    @{input}
    Should be equal    ${result}    ${expected}
    ${result} =    Join command line    ${input}
    Should be equal    ${result}    ${expected}
