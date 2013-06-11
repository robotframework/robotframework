*** Settings ***
Library           Process

*** Test Cases ***
No active process
    [Documentation]   FAIL   No active process.
    Wait For Process

No active process after run process
    [Documentation]   FAIL   No active process.
    Run Process     echo hello    shell=True
    Wait For Process

Invalid handle
    [Documentation]   FAIL   Non-existing index or alias 'non_existing'.
    Wait For Process    non_existing
