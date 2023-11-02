*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/InvalidKeywords.py
Resource          libdoc_resource.robot

*** Test Cases ***
Dublicate name
    Keyword Name Should Be    0    Duplicate Name
    Keyword Doc Should Be     0    *Creating keyword failed:* Keyword with same name defined multiple times.
    Stdout should contain adding keyword error
    ...    Duplicate Name
    ...    Keyword with same name defined multiple times.

Dublicate name with embedded arguments
    Keyword Name Should Be    1    Same \${embedded}
    Keyword Doc Should Be     1    ${EMPTY}
    Keyword Name Should Be    2    same \${match}
    Keyword Doc Should Be     2    This is an error only at run time.

Invalid embedded arguments
    Keyword Count Should Be    3
    Stdout should contain adding keyword error
    ...    Invalid embedded \${args}
    ...    Keyword must accept at least as many positional arguments as it has embedded arguments.

*** Keywords ***
Stdout should contain adding keyword error
    [Arguments]    ${name}    ${error}
    Should Contain    ${OUTPUT}
    ...    [ ERROR ] Error in library 'InvalidKeywords': Adding keyword '${name}' failed: ${error}
