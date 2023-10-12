*** Settings ***
Resource          atest_resource.robot
Resource          ../../libdoc/libdoc_resource.robot

*** Variables ***
${PORT FILE}      %{TEMPDIR}${/}remote_port.txt
${STDOUT FILE}    %{TEMPDIR}${/}remote_output.txt

*** Keywords ***
Run Remote Tests
    [Arguments]    ${tests}    ${server}    ${stop server}=yes
    ${port} =    Start Remote Server    ${server}
    Run Tests    --variable PORT:${port}    standard_libraries/remote/${tests}
    [Teardown]    Run Keyword If    '${stop server}' == 'yes'
    ...    Stop Remote Server    ${server}
    RETURN    ${port}

Start Remote Server
    [Arguments]    ${server}    ${port}=0
    Remove File    ${PORT FILE}
    ${path} =    Normalize Path    ${DATADIR}/standard_libraries/remote/${server}
    ${python} =    Evaluate    sys.executable    modules=sys
    Start Process    ${python}    ${path}    ${port}    ${PORT FILE}
    ...    alias=${server}    stdout=${STDOUT FILE}    stderr=STDOUT
    Wait Until Created    ${PORT FILE}    30s
    ${port} =    Get File    ${PORT FILE}
    RETURN    ${port}

Stop Remote Server
    [Arguments]    ${server}
    ${result} =    Terminate Process    handle=${server}
    Log    ${result.stdout}
