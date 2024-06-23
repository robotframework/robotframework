*** Test Cases ***
Scopes 3
    Variable Should Not Exist    ${SUITE}
    Should Be Equal    ${SUITES}    set in root suite setup    # set in root, changes in suite1 not seen here
    Should Be Equal    ${GLOBAL}    set in suite1 teardown     # set in root, changed in suite2
    Should Be Equal    ${ROOT}      set in root suite setup    # set in root, not changed
