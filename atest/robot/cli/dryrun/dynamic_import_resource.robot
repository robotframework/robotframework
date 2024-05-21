*** Settings ***
Resource         atest_resource.robot

*** Test Cases ***
Run imported keyword in dryrun mode
    Run Tests    --dryrun    cli/dryrun/dynamic_import_resource.robot
    Should be equal    ${SUITE.status}    PASS
