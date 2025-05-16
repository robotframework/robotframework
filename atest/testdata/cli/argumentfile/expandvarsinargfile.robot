*** Settings ***
Documentation     Tests for environment variable expansion in argument files
Library           OperatingSystem
Library           Process

*** Variables ***
${ARGDIR}         ${EXECDIR}${/}atest/testdata/cli/argumentfile

*** Test Cases ***
No Expansion By Default
    ${result}=    Run Process    python    -m    robot    --argumentfile    ${ARGDIR}${/}test_default.args    shell=True
    Log    ${result.stdout}
    Log    ${result.stderr}
    ${combined_output}=    Catenate    SEPARATOR=\n    ${result.stdout}    ${result.stderr}
    Should Contain    ${combined_output}    Example
    Should Not Contain    ${combined_output}    $TEST_DIR/output.xml
    Should Not Contain    ${combined_output}    \${TEST_DIR}/log.html

Expansion With Pragma True
    Set Environment Variable    TEST_DIR    test_output
    ${result}=    Run Process    python    -m    robot    --argumentfile    ${ARGDIR}${/}test_expandtrue.args    shell=True
    Log    ${result.stdout}
    Log    ${result.stderr}
    ${combined_output}=    Catenate    SEPARATOR=\n    ${result.stdout}    ${result.stderr}
    Should Contain    ${combined_output}    Example
    Should Contain    ${combined_output}    test_output/output.xml
    Should Contain    ${combined_output}    test_output/log.html


Double Expansion With Pragma True
    Set Environment Variable    TEST_DIR    test_output
    Set Environment Variable    TEST_DIR2    test_output2
    ${result}=    Run Process    python    -m    robot    --argumentfile    ${ARGDIR}${/}test_doubleexpandtrue.args    shell=True
    Log    ${result.stdout}
    Log    ${result.stderr}
    ${combined_output}=    Catenate    SEPARATOR=\n    ${result.stdout}    ${result.stderr}
    Should Contain    ${combined_output}    Example
    Should Contain    ${combined_output}    test_output/test_output2/output.xml
    Should Contain    ${combined_output}    test_output/test_output2/log.html

Expansion With Pragma False
    Set Environment Variable    TEST_DIR    test_output
    ${result}=    Run Process    python    -m    robot    --argumentfile    ${ARGDIR}${/}test_expandfalse.args    shell=True
    Log    ${result.stdout}
    Log    ${result.stderr}
    ${combined_output}=    Catenate    SEPARATOR=\n    ${result.stdout}    ${result.stderr}
    Should Contain    ${combined_output}    Example
    Should Contain    ${combined_output}    $TEST_DIR/output.xml
    Should Contain    ${combined_output}    \${TEST_DIR}/log.html
