*** Settings ***
Suite Setup       Run Tests
...      --variable WINDOWS:${INTERPRETER.is_windows} --ConsoleMarkers OFF
...      standard_libraries/builtin/import_resource.robot standard_libraries/builtin/import_variables.robot    default options=
Resource          atest_resource.robot

*** Test Cases ***
Resource import should work without configured --pythonpath
    Check Test Case    Import Resource In Suite Setup
    Check Test Case    Import Resource With Sub Resources
    Check Test Case    Import Resource In Test Case
    Check Test Case    Import Resource In User Keyword
    Check Test Case    Variables And Keywords Imported In Test Are Available In Next
    Check Test Case    Re-Import Resource

Variable import should work without configured --pythonpath
    Check Test Case    Import Variables In Suite Setup
    Check Test Case    Import Variables 1
    Check Test Case    Import Variables With Arguments
    Check Test Case    Import Variables In User Keyword 1
    Check Test Case    Re-Import Variables
    Check Test Case    Import Variables Arguments Are Resolved Only Once
