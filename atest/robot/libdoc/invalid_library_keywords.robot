*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/InvalidKeywords.py
Resource          libdoc_resource.robot

*** Test Cases ***
Dublicate name
    Keyword Name Should Be    0    Duplicate Name
    Keyword Doc Should Be     0    *Creating keyword failed:* Keyword with same name defined multiple times.
    Stdout should contain error    Duplicate Name    Keyword with same name defined multiple times

Dublicate name with embedded arguments
    Keyword Name Should Be    1    Same \${embedded}
    Keyword Doc Should Be     1    ${EMPTY}
    Keyword Name Should Be    2    same \${match}
    Keyword Doc Should Be     2    This is an error only at run time.

Invalid embedded arguments
    Keyword Count Should Be    3
    ${error} =    Catenate
    ...    [ ERROR ] Adding keyword 'Invalid embedded \${args}' to library 'InvalidKeywords' failed:
    ...    Embedded argument count does not match number of accepted arguments.
    Should Contain    ${OUTPUT}    ${error}

*** Keywords ***
Stdout should contain error
    [Arguments]    ${name}    ${error}
    ${message} =    Catenate
    ...    [ ERROR ] Error in test library 'InvalidKeywords':
    ...    Creating keyword '${name}' failed: ${error}
    Should Contain    ${OUTPUT}    ${message}
