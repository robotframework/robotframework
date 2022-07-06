*** Settings ***
Library           ParameterLibrary.V1    ${WITH NAME}    foo
Library           ParameterLibrary.V2    @{LIST AS}

*** Variables ***
${WITH NAME}      WITH NAME
@{LIST AS}        AS    bar

*** Test Cases ***
'WITH NAME' cannot come from variable
    ParameterLibrary.V1.Parameters should be    WITH NAME    foo
    ParameterLibrary.V2.Parameters should be    AS    bar

'WITH NAME' cannot come from variable with 'Import Library' keyword
    Import Library    ParameterLibrary.V3    ${WITH NAME}    zap
    Import Library    ParameterLibrary.V4    @{LIST AS}
    ParameterLibrary.V3.Parameters should be    WITH NAME    zap
    ParameterLibrary.V4.Parameters should be    AS    bar

'WITH NAME' cannot come from variable with 'Import Library' keyword even when list variable opened
    @{must open to find name} =    Create List    Import Library    ParameterLibrary.V5    ${WITH NAME}    foo
    Run Keyword    @{must open to find name}
    ParameterLibrary.V5.Parameters should be    WITH NAME    foo
    @{must open to find name} =    Create List    Import Library    ParameterLibrary.V6    @{LIST AS}
    Run Keyword    @{must open to find name}
    ParameterLibrary.V6.Parameters should be    AS    bar
