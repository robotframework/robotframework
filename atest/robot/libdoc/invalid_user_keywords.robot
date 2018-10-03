*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/invalid_user_keywords.robot
Resource          libdoc_resource.robot

*** Test Cases ***
Invalid arg spec
    Keyword Name Should Be    0    Invalid arg spec
    Keyword Doc Should Be     0    *Creating keyword failed:* Invalid argument specification: Only last argument can be kwargs.
    Stdout should contain error    Invalid arg spec    Invalid argument specification: Only last argument can be kwargs.

Dublicate name
    Keyword Name Should Be    3    Same twice
    Keyword Doc Should Be     3    *Creating keyword failed:* Keyword with same name defined multiple times.
    Stdout should contain error    Same twice    Keyword with same name defined multiple times

Dublicate name with embedded arguments
    Keyword Name Should Be    1    same \${embedded match}
    Keyword Doc Should Be     1    ${EMPTY}
    Keyword Name Should Be    2    Same \${embedded}
    Keyword Doc Should Be     2    This is an error only at run time.

*** Keywords ***
Stdout should contain error
    [Arguments]    ${name}    ${error}
    ${path} =    Normalize Path    ${DATADIR}/libdoc/invalid_user_keywords.robot
    ${message} =    Catenate
    ...    [ ERROR ] Error in resource file '${path}':
    ...    Creating keyword '${name}' failed: ${error}
    Should Contain    ${OUTPUT}    ${message}
