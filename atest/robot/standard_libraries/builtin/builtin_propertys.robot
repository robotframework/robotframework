*** Settings ***
Resource          atest_resource.robot

*** Test Cases ***
Normal run
    Run Tests    ${EMPTY}    standard_libraries/builtin/builtin_propertys.robot
    Check Test Case    Test propertys

Dry-run
    Run Tests    --dryrun --variable DRYRUN:True    standard_libraries/builtin/builtin_propertys.robot
    Check Test Case    Test propertys
