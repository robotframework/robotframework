*** Settings ***
Library           debugfile_writer.py
Library           OperatingSystem
*** Variables ***
${DEBUGFILE}      debug.log
*** Test Cases ***
log from thread process and async
      write_to_debugfile_from_thread
      Wait Until Keyword Succeeds	1 sec	0.01 sec	check for log entry         MainProcess\tThread-1 (write_to_debugfile)\tregular*Writing to debugfile from thread
      write_to_debugfile_from_process
      Wait Until Keyword Succeeds	1 sec	0.01 sec	check for log entry         Process-2\tMainThread\tregular*Writing to debugfile from process
      write_to_debugfile_from_async
      Wait Until Keyword Succeeds	1 sec	0.01 sec	check for log entry         MainProcess\tMainThread\tasync*Writing to debugfile from async


*** keywords ***
check for log entry
    [Arguments]    ${log}
    ${found} =	Grep File	${DEBUGFILE}         ${log}
    Should not be empty    ${found}
