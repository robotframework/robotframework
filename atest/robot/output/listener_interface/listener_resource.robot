*** Settings ***
Resource        atest_resource.robot

*** Variables ***
${ALL_FILE}  listen_all.txt
${ALL_FILE2}  listen_all2.txt
${SOME_FILE}  listen_some.txt
${JAVA_FILE}  listen_java.txt
${ARGS_FILE}  listener_with_args.txt
${JAVA_ARGS_FILE}  java_listener_with_args.txt
${MODULE_FILE}  listen_by_module.txt
${ATTR_TYPE_FILE}  listener_attrs.txt
${JAVA_ATTR_TYPE_FILE}  listener_attrs_java.txt
${SUITE_MSG}  1 critical test, 1 passed, 0 failed\n 2 tests total, 1 passed, 1 failed
${SUITE_MSG_2}  2 critical tests, 1 passed, 1 failed\n 2 tests total, 1 passed, 1 failed
${LISTENERS}  ${CURDIR}${/}..${/}..${/}..${/}testresources${/}listeners
${EMPTY TB}     \nTraceback (most recent call last):\n${SPACE*2}None\n

*** Keywords ***

Listener Import Message Should Be In Syslog
    [Arguments]  ${type}  ${name or path}  ${source}=    ${count}=1    ${deprecated}=None
    ${name or path} =    Normalize Path    ${name or path}
    ${module_path} =    Join Path  ${LISTENERS}  ${source}
    ${location} =    Set Variable If    '${source}'    '${module_path}    unknown location.
    ${syslog} =    Get syslog
    Should Contain X Times    ${syslog}    Imported listener ${type} '${name or path}' from ${location}    ${count}
    Run Keyword If    ${deprecated} is not None
    ...    Check Log Message    @{ERRORS}[${deprecated}]
    ...    Listener '${name or path}' uses deprecated API version 1. Switch to API version 2 instead.    WARN

Remove Listener Files
    Remove Files
    ...  %{TEMPDIR}${/}${ALL_FILE}
    ...  %{TEMPDIR}${/}${SOME_FILE}
    ...  %{TEMPDIR}${/}${JAVA_FILE}
    ...  %{TEMPDIR}${/}${ARGS_FILE}
    ...  %{TEMPDIR}${/}${ALL_FILE2}
    ...  %{TEMPDIR}${/}${MODULE_FILE}
    ...  %{TEMPDIR}${/}${JAVA_ARGS_FILE}
    ...  %{TEMPDIR}${/}${ATTR_TYPE_FILE}
    ...  %{TEMPDIR}${/}${JAVA_ATTR_TYPE_FILE}

Check Listener File
    [Arguments]  ${file}  @{expected}
    ${content} =  Get Listener File  ${file}
    ${exp} =  Catenate  SEPARATOR=\n  @{expected}
    Should Be Equal  '${content}'  '${exp}\n'

Get Listener FIle
    [Arguments]  ${file}
    ${content} =  Get File  %{TEMPDIR}/${file}
    [Return]  ${content}

