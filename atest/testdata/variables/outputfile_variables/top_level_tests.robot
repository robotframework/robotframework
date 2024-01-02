*** Variables ***
@{VARIABLES}      ${OUTPUT DIR}    ${OUTPUT FILE}    ${LOG FILE}    ${REPORT FILE}    ${DEBUG FILE}

*** Test Cases ***
Log All Output Files In Toplevel
    Log Many    @{VARIABLES}

Result file variables are strings
    FOR    ${var}    IN    @{VARIABLES}
        Should Be True    isinstance($var, str)
        ...    msg='${var}' is ${{type($var).__name__}}, not string.
        Should Be True    os.path.isabs($var) or $var == 'NONE'
        ...    msg='${var}' is not absolute or 'NONE'
    END
