*** Setting ***
Suite Setup       Run Tests    \    variables${/}reserved_syntax.html
Force Tags        pybot    jybot    regression
Resource          atest_resource.txt

*** Variable ***

*** Test Case ***
Reserved Syntax &{var}
    Check Test Case    Reserved Syntax \&{var}

Reserved Syntax *{var}
    Check Test Case    Reserved Syntax \*{var}

There should Be A Warning About Using Reserved Syntax In Stderr
    ${stderr} =    Get Stderr
    ${exp1} =    Catenate    Syntax '\&{this_causes_warning}' is reserved for future use.    Please escape it like '\\\&{this_causes_warning}'.
    ${exp2} =    Catenate    Syntax '\*{this_causes_warning}' is reserved for future use.    Please escape it like '\\\*{this_causes_warning}'.
    Should Be Equal    ${stderr}    [ WARN ] ${exp1}\n [ WARN ] ${exp2}\n

*** Keyword ***
