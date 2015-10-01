*** Settings ***
Resource          console_resource.robot

*** Variables ***
${TEST FILE}      ${DATADIR}/misc/pass_and_fail.robot
${STDOUT FILE}    %{TEMPDIR}/redirect_stdout.txt
${STDERR FILE}    %{TEMPDIR}/redirect_stderr.txt

*** Test Cases ***
Invalid Encoding In Environment Variables
    [Tags]    no-windows
    ${stdout}    ${stderr} =    Run Some Tests With Std Streams Redirected
    Should Contain    ${stdout}    Pass And Fail :: Some tests here

*** Keywords ***
Run Some Tests With Std Streams Redirected
    ${cmd} =    Join command line
    ...    LANG=invalid
    ...    LC_TYPE=invalid
    ...    LANGUAGE=invalid
    ...    LC_ALL=invalid
    ...    @{INTERPRETER.runner}
    ...    --output    NONE
    ...    --report    NONE
    ...    --log    NONE
    ...    --consolecolors    off
    ...    ${TESTFILE}
    Run Process    echo "redirect stdin" | ${cmd}    shell=True    stdout=${STDOUT FILE}    stderr=${STDERR FILE}
    ${stdout} =    Log File    ${STDOUT FILE}
    ${stderr} =    Log File    ${STDERR FILE}
    [Return]    ${stdout}    ${stderr}
