*** Settings ***
Library           debugfile_writer.py
Library           OperatingSystem
*** Test Cases ***
from thread
      write_to_debugfile_from_thread
      ${found} =	Grep File	debug.log         MainProcess\tThread-1 (write_to_debugfile)\tregular*Writing to debugfile from thread
      Should not be empty    ${found}

from process
      write_to_debugfile_from_process
      ${found} =	Grep File	debug.log         Process-2\tMainThread\tregular*Writing to debugfile from process
      Should not be empty    ${found}

from async
    write_to_debugfile_from_async
    ${found} =	Grep File	debug.log         MainProcess\tMainThread\tasync*Writing to debugfile from async
    Should not be empty    ${found}