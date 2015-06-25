*** Settings ***
Force Tags        regression    pybot    jybot
Resource          libdoc_resource.robot

*** Test Cases ***
List all keywords
    Run Libdoc And Verify Output    Dialogs list
    ...   Execute Manual Step
    ...   Get Selection From User
    ...   Get Value From User
    ...   Pause Execution

List some keywords
    Run Libdoc And Verify Output    ${TESTDATADIR}/resource.robot list o
    ...   Keyword with some "stuff" to <escape>
    ...   non ascii doc
    Run Libdoc And Verify Output    ${TESTDATADIR}/resource.robot LIST KW? C*R
    ...   curdir
    ...   kw 3
    ...   kw 4
    ...   kw 5
    ...   kw 6

Show whole library
    Run Libdoc And Set Output    Dialogs show
    Should Contain Intro    Dialogs    Version:
    Should Contain Keyword    Execute Manual Step    message, default_error=
    ...    Pauses test execution until user sets the keyword status.
    Should Contain Keyword    Get Selection From User    message, *values
    ...    Pauses test execution and asks user to select a value.
    Should Contain Keyword    Get Value From User    message, default_value=, hidden=False
    ...    Pauses test execution and asks user to input a value.
    Should Contain Keyword    Pause Execution    message=Test execution paused. Press OK to continue.
    ...   Pauses test execution until user clicks ``Ok`` button.
    ...   ${EMPTY}
    ...   ``message`` is the message shown in the dialog.

Show intro only
    Run Libdoc and set output    Telnet SHOW intro
    Should Contain Intro    Telnet    Version:
    ${args} =    Catenate    SEPARATOR=\n${SPACE*12}
    ...    timeout=3 seconds, newline=CRLF, prompt=None,
    ...    prompt_is_regexp=False, encoding=UTF-8, encoding_errors=ignore,
    ...    default_log_level=INFO, window_size=None, environ_user=None,
    ...    terminal_emulation=False, terminal_type=None,
    ...    telnetlib_log_level=TRACE
    Should Contain Importing    ${args}
    ...    Telnet library can be imported with optional configuration parameters.
    Should Not Contain Keyword    Open Connection
    Should Not Contain Keyword    Write

Show intro and keywords
    Run Libdoc and set output    ${TESTDATADIR}/resource.robot SHOW NONASC* INTRO
    Should Contain Intro    resource    Named arguments:${SPACE*2}supported
    Should Contain Keyword    non ascii doc    ${EMPTY}
    ...    Hyvää yötä.
    ...    ${EMPTY}
    # Cannot test does output contain `Спасибо!` because consoles may not be able to show it.
    # Actually all consoles cannot show `Hyvää yötä` either but we expect western config.

Show version
    Run Libdoc And Verify Output    ${TESTDATADIR}/module.py version    0.1-alpha
    Run Libdoc And Verify Output    ${TESTDATADIR}/resource.robot version    N/A

*** Keywords ***
Should Contain Intro
    [Arguments]    ${name}    @{meta}
    ${underline} =    Evaluate    '='*len('${name}')
    ${expected} =    Catenate    SEPARATOR=\n
    ...    ${name}
    ...    ${underline}
    ...    @{meta}
    Should Contain    ${OUTPUT}    ${expected}

Should Contain Keyword
    [Arguments]    ${name}    ${args}    @{doc}
    ${underline} =    Evaluate    '-'*len('${name}')
    ${expected} =    Catenate    SEPARATOR=\n
    ...    ${name}
    ...    ${underline}
    ...    Arguments:${SPACE * 2}[${args}]
    ...    ${EMPTY}
    ...    @{doc}
    Should Contain    ${OUTPUT}    ${expected}

Should Contain Importing
    [Arguments]    ${args}    @{doc}
    Should Contain Keyword    Importing    ${args}    @{doc}

Should Not Contain Keyword
    [Arguments]    ${name}
    ${underline} =    Evaluate    '-'*len('${name}')
    ${expected} =    Catenate    SEPARATOR=\n
    ...    ${name}
    ...    ${underline}
    Should Not Contain    ${OUTPUT}    ${expected}
