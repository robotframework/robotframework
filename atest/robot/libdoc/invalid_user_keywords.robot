*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/invalid_user_keywords.robot
Force Tags        regression    pybot    jybot
Resource          libdoc_resource.robot

*** Test Cases ***
Dublicate name
    Keyword Name Should Be    2    Same twice
    Keyword Doc Should Be     2    *Creating keyword failed: Keyword with same name defined multiple times.*
    Should Contain    ${OUTPUT}    [ ERROR ] Creating user keyword 'Same twice' failed: Keyword with same name defined multiple times

Dublicate name with embedded arguments
    Keyword Name Should Be    1     same \${embedded match}
    Keyword Doc Should Be     1    *Creating keyword failed: Keyword with same name defined multiple times.*
    Should Contain    ${OUTPUT}    [ ERROR ] Creating user keyword 'same \${embedded match}' failed: Keyword with same name defined multiple times

Invalid arg spec
    Keyword Name Should Be    0     Invalid arg spec
    Keyword Doc Should Be     0    *Creating keyword failed: Invalid argument specification: Positional argument after varargs.*
    Should Contain    ${OUTPUT}    [ ERROR ] Creating user keyword 'Invalid arg spec' failed: Invalid argument specification: Positional argument after varargs.
