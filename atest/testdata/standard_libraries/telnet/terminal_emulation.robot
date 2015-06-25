*** Setting ***
Test Setup        Login and set prompt
Test Teardown     Close All Connections
Library           Telnet    3.142    CRLF    $    REGEXP    ASCII    strict    DeBuG    terminal_emulation=yes   terminal_type=vt100
Library           String
Resource          telnet_resource.robot

*** Variables ***
${=}=    =

*** Test Cases ***

Execute command
    ${output}=    Execute Command    echo -e "abba\\x1b[3Dcdc"
    Should Match   ${output}    acdc\r\n*

Read Until Regex
    Write    echo -e "abba\\x1b[3Dcdc"
    Read Until Regexp    acdc

Read Until Multiple Regexp
    Write    echo -e "abba\\x1b[3Dcdc"
    Read Until Regexp    foo    acdc    bar

Reads Only the Necessary Amount
    Write    echo -e "abba\\x1b[3Dcdc_foo_bar_dar"
    Read Until Regexp Should match    acdc    acdc
    Read Until should match    _foo      foo
    Read Until should match     _bar      bar
    Read Until regexp should match   _dar    dar

Reads Only the Necessary Amount with rewrites
    Write    echo -e "abba\\x1b[3Dcdc_foo_"
    Read Until Regexp Should match    acdc    acdc
    Write Bare    echo -e "abba\\x1b[3Ddhd_bar_"\r\n
    Read Until Regexp Should match    _foo_*adhd    adhd
    Write Bare    echo -e "abba\\x1b[3Dmma_more"\r\n
    Read until Should Match    _bar_*amma     amma
    Read Until Should match    _more          more

Empties buffer on not found read until
    Write    echo abba
    Run keyword and expect error    No match found *      Read until    not there
    Write bare      token
    Read until should match    token     token

Empties buffer on not found read until regexp
    Write    echo abba
    Run keyword and expect error    No match found *      Read until regexp    not there
    Write bare      token
    Read until regexp should match    token     token

Read
    Write    echo -e "abba\\x1b[3Dcdc"
    Read Should Match     acdc*
    Write bare      token
    Sleep       0.1    # We cant wait until output, because the whole idea is to test "read"
    Read should match    token

Read Until Reads Using Internal Update Frequency
    Write    echo -e "abba\\x1b[3Dcdc"
    Set timeout    2
    Run with timeout 0.5    Read Until     acdc

Read Until Regexp Using Internal Update Frequency
    Write    echo -e "abba\\x1b[3Dcdc"
    Set timeout    2
    Run with timeout 0.5    Read Until Regexp    acdc

Window Size
    [Setup]    Login and set prompt    terminal_emulation=True   window_size=1024x1024
    Set Timeout   5
    Execute Command    echo $TERM
    Execute Command    stty -a
    Write    echo ${=*1000}
    Read Should Match     ${=*1000}*

Window Size 100x80
    [Setup]    Login and set prompt    terminal_emulation=True   window_size=100x80
    Set Timeout   5
    Execute Command    stty -a
    Write    echo ${=*90}
    Read Should Match     ${=*90}*

Override terminal emulation and type
    [Setup]    Login and set prompt    terminal_emulation=False   terminal_type=network
    ${output}=    Execute Command    echo -e "abba\\x1b[3Dcdc"
    Should Match   ${output}    abba\x1b[3Dcdc\r\n*
    Environment variable should be    $TERM    network

Pagination
    [Setup]    Login and set prompt    terminal_emulation=True   window_size=80x10
    Write bare    echo -e "abba\\x1b[3Dcdc\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\nline11"\n
    ${out}=       Read until prompt
    Should match    ${out}    *\r\nacdc\r\nline2\r\nline3\r\nline4\r\nline5\r\nline6\r\nline7\r\nline8\r\nline9\r\nline10\r\nline11\r\n*

Lots and lots of pages
    Set timeout    20
    ${out}=       Execute command     python -c "print 'abba\\x1b[3Dcdc\\n'*20000"
    Should contain x times    ${out}    acdc\r\n    20000

Write & Read Non-ASCII
    [Setup]    Login and set prompt   terminal_emulation=True   terminal_type=vt100  encoding=UTF-8
    Write    echo Hyvää yötä    wArN
    ${out} =    Read until prompt    deBug
    Should Be Equal    ${out}    Hyvää yötä\r\n${FULL PROMPT}

Write & Read non-ISO-LATIN-1
    [Setup]    Login and set prompt   terminal_emulation=True   terminal_type=vt100  encoding=UTF-8
    Write    echo \u2603    wArN
    ${out} =    Read until prompt    deBug
    Should Be Equal    ${out}    \u2603\r\n${FULL PROMPT}

Write ASCII-Only Unicode When Encoding Is ASCII
    [Documentation]   FAIL STARTS: UnicodeEncodeError:
    Write    echo Only ASCII
    ${out} =    Read Until Prompt
    Should Be Equal    ${out}    Only ASCII\r\n${FULL PROMPT}
    Write    Tämä ei toimi

Encoding can not be changed in terminal encoding
    [Documentation]   FAIL STARTS: Encoding can not be changed when terminal emulation is used
    Set encoding   UTF-8

Newline can not be changed in terminal encoding
    [Documentation]   FAIL STARTS: Newline can not be changed when terminal emulation is used
    Set newline       LF

*** Keywords ***
Run with timeout 0.5
    [Arguments]    ${kw}    @{args}
    [Timeout]     0.5
    ${res}=   Run keyword    ${kw}    @{args}
    [Return]    ${res}

Read until should match
    [Arguments]    ${expected}   ${match}
    ${output}=      Read until   ${match}
    Should match    ${output}    ${expected}

Read until regexp should match
    [Arguments]    ${expected}     @{match}
    ${output}=      Read until regexp   @{match}
    Should match    ${output}    ${expected}

Read Should Match
    [Arguments]    ${expected}
    ${output}=      Read
    Should match    ${output}    ${expected}
