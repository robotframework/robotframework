*** Settings ***
Library           debugfile_writer.py
Library           OperatingSystem
*** Variables ***
${DEBUGFILE}      debug.log
*** Test Cases ***
log from thread
      ${major}    ${minor}    ${patch} =    Evaluate    sys.version_info[:3]    modules=sys
      Run Keyword If    $major >= 3 and $minor >= 10     write_to_debugfile_from_thread
      Run Keyword If    $major >= 3 and $minor >= 10     Wait Until Keyword Succeeds	1 sec	0.01 sec	check for log entry         MainProcess\tThread-1 (write_to_debugfile)\tregular*Writing to debugfile from thread

log from process
      ${PLATFORM} =      Evaluate    platform.system()    modules=platform
      Run Keyword If    $PLATFORM == 'Linux'     write_to_debugfile_from_process
      Run Keyword If    $PLATFORM == 'Linux'     Wait Until Keyword Succeeds	1 sec	0.01 sec	check for log entry         Process-2\tMainThread\tregular*Writing to debugfile from process

log from async
      ${major}    ${minor}    ${patch} =    Evaluate    sys.version_info[:3]    modules=sys
      Run Keyword If    $major >= 3 and $minor >= 10     write_to_debugfile_from_async
      Run Keyword If    $major >= 3 and $minor >= 10     Wait Until Keyword Succeeds	1 sec	0.01 sec	check for log entry         MainProcess\tMainThread\tasync*Writing to debugfile from async

*** keywords ***
check for log entry
    [Arguments]    ${log}
    ${found} =	Grep File	${DEBUGFILE}         ${log}
    Should not be empty    ${found}
