*** Settings ***
Force Tags        regression    pybot    jybot
Resource          rebot_cli_resource.robot
Suite Setup       Run Keywords
...               Run tests to create input file for Rebot    ${TESTS}    ${INPUT}    AND
...               Set Environment Variable    REBOT_OPTIONS    --name Default --settag default
Suite Teardown    Delete Environment Variable    REBOT_OPTIONS

*** Variables ***
${TESTS}          misc/pass_and_fail.robot
${INPUT}          %{TEMPDIR}${/}rebot_options.xml

*** Test Cases ***
Use defaults
    Run Rebot    ${EMPTY}    ${INPUT}
    Should Be Equal    ${SUITE.name}    Default
    Check Test Tags    Pass    force    pass    default

Override defaults
    Run Rebot    -N Given -G given   ${INPUT}
    Should Be Equal    ${SUITE.name}    Given
    Check Test Tags    Pass    force    pass    default    given
