*** Settings ***
Suite Setup     Run Tests  --dryrun  cli/dryrun/run_keyword_variants_in_suite_teardown.robot
Resource        atest_resource.robot


*** Test Cases ***

Suite Teardown Related Run Keyword Variants
    Check Test Case  ${TESTNAME}

