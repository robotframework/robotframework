*** Settings ***
Library           debugfile_writer.py
Library           OperatingSystem
*** Variables ***
${DEBUGFILE}      debug.log
*** Test Cases ***
log from thread process and async
      write_to_debugfile_from_thread
      ${found} =	Grep File	${DEBUGFILE}         MainProcess\tThread-1 (write_to_debugfile)\tregular*Writing to debugfile from thread
      Should not be empty    ${found}
      write_to_debugfile_from_process
      ${found} =	Grep File	${DEBUGFILE}         Process-2\tMainThread\tregular*Writing to debugfile from process
      Should not be empty    ${found}
      write_to_debugfile_from_async
      ${found} =	Grep File	${DEBUGFILE}         MainProcess\tMainThread\tasync*Writing to debugfile from async
      Should not be empty    ${found}
