*** Settings ***
Resource          cli_resource.robot
Suite Setup       Set Environment Variable    ROBOT_OPTIONS    --name Default --settag "default with spaces" --dryrun
Suite Teardown    Remove Environment Variable    ROBOT_OPTIONS

*** Test Cases ***
Use defaults
    Run Tests    ${EMPTY}    misc/pass_and_fail.robot
    Should Be Equal    ${SUITE.name}    Default
    ${tc} =    Check Test Tags    Pass    force    pass    default with spaces
    Should Be Equal    ${tc.kws[0].kws[0].status}    NOT RUN

Override defaults
    Run Tests    -N Given -G given --nodryrun    misc/pass_and_fail.robot
    Should Be Equal    ${SUITE.name}    Given
    ${tc} =    Check Test Tags    Pass    force    pass    default with spaces    given
    Should Be Equal    ${tc.kws[0].kws[0].status}    PASS
