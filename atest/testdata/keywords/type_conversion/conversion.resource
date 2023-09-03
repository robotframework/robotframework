*** Variables ***
${CUSTOM}         ${{type('Custom', (), {})()}}

*** Keywords ***
Conversion Should Fail
    [Arguments]    ${kw}    @{args}    ${error}=    ${type}=${kw.lower()}    ${arg_type}=    &{kwargs}
    ${arg} =    Evaluate    (list($args) + list($kwargs.values()))[0]
    ${message} =    Catenate
    ...     ValueError:
    ...     Argument 'argument' got value '${arg}'${{" (${arg_type})" if $arg_type else ""}}
    ...     that cannot be converted to ${type}${{": ${error}" if $error else "."}}
    TRY
        Run Keyword    ${kw}    @{args}    &{kwargs}
    EXCEPT    ${message}    type=${{'GLOB' if '*' in $error else 'LITERAL'}}
        No Operation
    EXCEPT    AS    ${err}
        Fail    Expected error\n\n \ ${message}\n\nbut got\n\n \ ${err}
    ELSE
        Fail    Expected error '${message}' did not occur.
    END

String None is converted to None object
    [Arguments]    ${kw}
    Run Keyword    ${kw}    None       ${None}
    Run Keyword    ${kw}    NONE       ${None}
    Run Keyword    ${kw}    none       ${None}
