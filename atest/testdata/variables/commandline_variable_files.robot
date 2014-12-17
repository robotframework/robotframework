*** Variables ***
@{EXPECTED LIST}  List  variable  value

*** Test Cases ***
Variables From Variable File
    Should Be Equal  ${SCALAR}  Scalar from variable file from CLI
    Should Be Equal  ${SCALAR WITH ESCAPES}  1 \\ 2\\\\ \${inv}
    Should Be Equal  ${SCALAR LIST}  ${EXPECTED LIST}
    Should Be True  @{LIST} == ${EXPECTED LIST}

Arguments To Variable Files
    Should Be Equal  ${ANOTHER SCALAR}  Variable from CLI var file with get_variables
    Should Be True  @{ANOTHER LIST} == ['List variable from CLI var file', 'with get_variables']
    Should Be Equal  ${ARG}  default value
    Should Be Equal  ${ARG 2}  value;with;semi;colons

Arguments To Variable Files Using Semicolon Separator
    Should Be Equal  ${SEMICOLON}  separator
    Should Be Equal  ${SEMI:COLON}  separator:with:colons

Variable File From PYTHONPATH
    Should Be Equal  ${PYTHONPATH VAR 0}  Varfile found from PYTHONPATH
    Should Be Equal  ${PYTHONPATH ARGS 0}  ${EMPTY}

Variable File From PYTHONPATH with arguments
    Should Be Equal  ${PYTHONPATH VAR 3}  Varfile found from PYTHONPATH
    Should Be Equal  ${PYTHONPATH ARGS 3}  1-2-3
