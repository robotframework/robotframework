*** Settings ***
Test Setup        Login And Set Prompt
Test Teardown     Close All Connections
Library           Telnet    newline=CRLF
Library           String
Resource          telnet_resource.robot

*** Variables ***
${TIMEOUT}        300 milliseconds

*** Test Cases ***
Write & Read
    ${text} =    Write    pwd
    Should Be Equal    ${text}    pwd\r\n
    Sleep    300 ms
    ${out} =    Read
    Should Be Equal    ${out}    ${HOME}\r\n${FULL PROMPT}

Write & Read Non-ASCII
    Write    echo Hyvää yötä    wArN
    Sleep    300 ms
    ${out} =    Read    deBug
    Should Be Equal    ${out}    Hyvää yötä\r\n${FULL PROMPT}

Write & Read Non-ASCII Bytes
    Set Encoding    NONE
    ${bytes} =    Encode String To Bytes   echo Hyvää yötä    UTF-8
    Write    ${bytes}
    ${out} =    Read Until Prompt
    Should Be Byte String    ${out}
    ${expected} =    Encode String To Bytes    Hyvää yötä\r\n${FULL PROMPT}    UTF-8
    Should Be Equal    ${out}    ${expected}
    [Teardown]    Set Encoding    UTF-8

Write ASCII-Only Unicode When Encoding Is Disabled
    [Documentation]   FAIL STARTS: UnicodeEncodeError:
    Set Encoding    NONE
    Write    echo Only ASCII
    ${out} =    Read Until Prompt
    Should Be Equal    ${out.decode('ASCII')}    Only ASCII\r\n${FULL PROMPT}
    Write    Tämä ei toimi

Write Does Not Allow Newlines
    [Documentation]    FAIL 'Write' keyword cannot be used with strings containing newlines. Use 'Write Bare' instead.
    Write    hello\r\nworld

Write Bare
    Write Bare    echo foo
    ${out} =    Read Until    oo
    Should Be Equal    ${out}    echo foo
    Write Bare    \r\n
    ${out} =    Read Until    oo
    Should Be Equal    ${out}    \r\nfoo

Write Bare With Newlines
    Write Bare    a=1\r\nb=2\r\necho $a $b 3\r\n
    ${out} =    Read Until    1 2 3
    Should Be Equal    ${out}    a=1\r\n${FULL PROMPT}b=2\r\n${FULL PROMPT}echo $a $b 3\r\n1 2 3

Write control character using name
    [Documentation]   FAIL STARTS: No match found for 'moi' in 300 milliseconds.
    Write     sleep 0.2;echo moi
    Write Control Character    IP
    Read until   moi

Write control character using number
    [Documentation]   FAIL STARTS: No match found for 'moi' in 300 milliseconds.
    Write     sleep 0.2;echo moi
    Write Control Character    244    # Same as IP
    Read until   moi

Read Until
    Write    pwd
    ${out} =    Read Until    /
    Should Be Equal    ${out}    /
    ${out} =    Read Until    /    DEBUG
    Should Be Equal    ${out}    home/

Read Until Non-ASCII
    Write    echo Hyvää yötä
    ${out} =    Read Until    yötä
    Should Be Equal    ${out}    Hyvää yötä

Read Until Fails
    [Documentation]    FAIL No match found for 'Not found' in ${TIMEOUT}. Output:\n
    Read Until    Not found

Read Until Regexp
    Write    pwd
    ${out} =    Read Until Regexp    /h[abo]me.${USERNAME}\\s+
    Should Be Equal    ${out}    ${HOME}\r\n
    ${out} =    Read Until Regexp    no match    .*@    blaah    deBUG
    Should Be Equal    ${out}    ${PROMPT START}

Read Until Regexp With Compiled Regexp
    Write    pwd
    ${regexp} =    Evaluate    re.compile('/h[abo]me.${USERNAME}\\s+')    modules=re
    ${out} =    Read Until Regexp    ${regexp}
    Should Be Equal    ${out}    ${HOME}\r\n
    ${regexp} =    Evaluate    re.compile('.*@')    modules=re
    ${out} =    Read Until Regexp    no match    ${regexp}    blaah    deBUG
    Should Be Equal    ${out}    ${PROMPT START}

Read Until Regexp Non-ASCII
    Write    echo Päivää
    ${out} =    Read Until Regexp    ei mätsää    ää    debug
    Should Be Equal    ${out}    Päivää

Read Until Regexp Fails
    [Documentation]    FAIL No match found for 'Not found' in ${TIMEOUT}. Output:\n
    Read Until Regexp    Not found

Read Until Regexp Requires At Least One Pattern
    [Documentation]    FAIL At least one pattern required
    Read Until Regexp

Read Until Prompt
    [Documentation]    FAIL Prompt '$$' not found in ${TIMEOUT}.
    Write    pwd
    ${out} =    Read Until Prompt
    Should Be Equal    ${out}    ${HOME}\r\n${FULL PROMPT}
    Write    pwd
    ${out} =    Read Until Prompt    dEbUg
    Should Be Equal    ${out}    ${HOME}\r\n${FULL PROMPT}
    Set Prompt    $$
    Write    pwd
    Read Until Prompt

Read Until Prompt And Strip Prompt
    Set Prompt  ${FULL PROMPT}
    Write    pwd
    ${out} =    Read Until Prompt    strip_prompt=${True}
    Should Be Equal    ${out}    ${HOME}\r\n
    Write    pwd
    ${out} =    Read Until Prompt    DEbug    non-empty-string
    Should Be Equal    ${out}    ${HOME}\r\n

Read Until Regexp Prompt
    [Documentation]    FAIL Prompt 'No match' not found in ${TIMEOUT}.
    Set Prompt    \\$\\s    REGEXP
    Write    pwd
    ${out} =    Read Until Prompt
    Should Be Equal    ${out}    ${HOME}\r\n${FULL PROMPT}
    Set Prompt    No match    true
    Write    pwd
    Read Until Prompt

Read Until Regexp Prompt And Strip Prompt
    Set Prompt    ${USERNAME}.*\\$\\s    REGEXP
    Write    pwd
    ${out} =    Read Until Prompt  strip_prompt=${True}
    Should Be Equal    ${out}    ${HOME}\r\n

Write Until Expected Output
    [Documentation]    FAIL No match found for 'Not found' in 300 milliseconds.
    Write    a=10
    Write Until Expected Output    a=$(($a - 1)); if (($a == 0)); then echo BLAST; fi\r\n    BLAST    2 s    10ms
    Write Until Expected Output    ls    Not found    300ms    100ms

Execute Command
    ${output} =    Execute Command    pwd
    Should Be Equal    ${output}    ${HOME}\r\n${FULL PROMPT}

Execute Command And Strip Prompt
    Set Prompt  ${FULL PROMPT}
    ${output} =    Execute Command    pwd    strip_prompt=${True}
    Should Be Equal    ${output}    ${HOME}\r\n
    ${output} =    Execute Command    pwd    debUG    ${True}
    Should Be Equal    ${output}    ${HOME}\r\n

Writing and reading fails if there is no connection
    [Setup]    NONE
    [Template]    Should fail because no connection
    Write    foo
    Write Bare    bar
    Write Until Expected Output    foo    bar    1s    0.1s
    Read
    Read Until    foo
    Read Until Regexp    bar
