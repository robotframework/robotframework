*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${ALL_FILE}       listen_all.txt
${ALL_FILE2}      listen_all2.txt
${SOME_FILE}      listen_some.txt
${ARGS_FILE}      listener_with_args.txt
${MODULE_FILE}    listen_by_module.txt
${ATTR_TYPE_FILE}    listener_attrs.txt
${SUITE_MSG}      2 tests, 1 passed, 1 failed
${SUITE_MSG_2}    2 tests, 1 passed, 1 failed
${LISTENERS}      ${CURDIR}${/}..${/}..${/}..${/}testresources${/}listeners
${EMPTY TB}       \nTraceback (most recent call last):\n${SPACE*2}None\n
${LISTENER DIR}   ${DATADIR}/output/listener_interface

*** Keywords ***
Listener Import Message Should Be In Syslog
    [Arguments]    ${type}    ${name or path}    ${source}=    ${count}=1
    ${name or path} =    Normalize Path    ${name or path}
    ${module_path} =    Join Path    ${LISTENERS}    ${source}
    ${location} =    Set Variable If    '${source}'    '${module_path}    unknown location.
    ${syslog} =    Get syslog
    Should Contain X Times    ${syslog}    Imported listener ${type} '${name or path}' from ${location}    ${count}

Remove Listener Files
    Remove Files
    ...    %{TEMPDIR}/${ALL_FILE}
    ...    %{TEMPDIR}/${SOME_FILE}
    ...    %{TEMPDIR}/${ARGS_FILE}
    ...    %{TEMPDIR}/${ALL_FILE2}
    ...    %{TEMPDIR}/${MODULE_FILE}
    ...    %{TEMPDIR}/${ATTR_TYPE_FILE}

Check Listener File
    [Arguments]    ${file}    @{expected}
    ${content} =    Get Listener File    ${file}
    ${expected} =    Catenate    SEPARATOR=\n    @{expected}    ${EMPTY}
    Should Be Equal    ${content}    ${expected}

Get Listener File
    [Arguments]    ${file}
    ${path} =    Join Path    %{TEMPDIR}    ${file}
    ${content} =    Get File    ${path}
    [Return]    ${content}
