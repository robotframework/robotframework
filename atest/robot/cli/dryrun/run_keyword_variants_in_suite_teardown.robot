*** Settings ***
Suite Setup     Run Tests  --dryrun  cli/dryrun/run_keyword_variants_in_suite_teardown.robot
Force Tags      regression  pybot  jybot
Resource        atest_resource.robot


*** Test Cases ***

Suite Teardown Related Run Keyword Variants
    Check Test Case  ${TESTNAME}

