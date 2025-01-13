*** Settings ***
Library           debugfile_writer.py
Library           OperatingSystem
Library           String
*** Variables ***
${DEBUGFILE}      debug.log
*** Test Cases ***
log from thread
      ${major}    ${minor}    ${patch} =    Evaluate    sys.version_info[:3]    modules=sys
      Run Keyword and expect Error          *           check for log entry         ^MainProcess\twr_thread\tstd_thread\t.*- DEBUG - Writing to debugfile from thread.*
      Run Keyword If    $major >= 3 and $minor >= 10     write_to_debugfile_from_thread
      Run Keyword If    $major >= 3 and $minor >= 10     Wait Until Keyword Succeeds	1 sec	0.01 sec	check for log entry         ^MainProcess\twr_thread\tstd_thread\t.*- DEBUG - Writing to debugfile from thread.*

log from process
      Run Keyword and expect Error       *                  check for log entry        ^wr_process\tMainThread\tstd_thread\t.*- DEBUG - Writing to debugfile from process.*
      write_to_debugfile_from_process
      Wait Until Keyword Succeeds	     1 sec	0.01 sec    check for log entry        ^wr_process\tMainThread\tstd_thread\t.*- DEBUG - Writing to debugfile from process.*

log from async
      ${major}    ${minor}    ${patch} =                               Evaluate                         sys.version_info[:3]    modules=sys
      Run Keyword and expect Error    *                                check for log entry              ^MainProcess\tMainThread\tasync_.*Writing to debugfile from async.*
      Run Keyword If                  $major >= 3 and $minor >= 10     write_to_debugfile_from_async
      Run Keyword If                  $major >= 3 and $minor >= 10     Wait Until Keyword Succeeds	  1 sec	              0.01 sec	check for log entry      ^MainProcess\tMainThread\tasync_.*Writing to debugfile from async.*

*** keywords ***
check for log entry
    [Arguments]    ${log}
    ${data} =	Get File	${DEBUGFILE}
    ${found}=     Get Lines Matching Regexp    ${data}     ${log}
    Should not be empty    ${found}
