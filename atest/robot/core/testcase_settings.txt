*** Settings ***
Suite Setup     My Setup
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***

Test Case Documentation
    Check Test Doc  Test Case Documentation  Documentation for this test case

Test Case Documentation In Multiple Columns
    Check Test Doc  Test Case Documentation in Multiple Columns  Documentation for this  test case in multiple columns

Test Case Documentation In Multiple Lines
    Check Test Doc  Test Case Documentation in Multiple Lines  Documentation for this  test case in multiple lines

Test Case Documentation With Variables
    Check Test Doc  Test Case Documentation With Variables  Variables work in documentation  since Robot 1.2

Test Case Documentation With Non-Existing Variables
    Check Test Doc  Test Case Documentation With Non-Existing Variables  Starting from RF 2.1 \${NONEX} variables are just left unchanged in all documentations.

*** Keywords ***
My Setup
    Run Tests  --variable suite_doc_from_cli:Hello --variable suite_fixture_from_cli:Log --variable meta_from_cli:my_metadata  core/testcase_settings.txt

