*** Test Cases ***
Reserved Syntax *{var}
    ${*} =    Set Variable    *
    Should Be Equal    *{this_causes_warning}    ${*}{this_causes_warning}
    Should Be Equal    \*{no_warning}    *\{no_warning}

Reserved With Variable Indise
    ${var} =    Set Variable    Hello
    Should Be Equal    *{${var}, world!}    \*{Hello, world!}
