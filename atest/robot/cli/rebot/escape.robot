*** Settings ***
Suite Setup       Run tests with escaping
Resource          rebot_cli_resource.robot

*** Test Cases ***
--escape options and arguments
    Should be equal    ${SUITE.name}    * name *
    Should be equal    ${SUITE.doc}    @@
    Should contain tests    ${SUITE}    Pass

--escape is deprecated
    Stderr Should Be Equal To    [ WARN ] Option '--escape' is deprecated. Use console escape mechanism instead.\n

*** Keywords ***
Run tests with escaping
    Run tests to create input file for Rebot    misc/pass_and_fail.robot
    ${opts} =    Catenate
    ...    --escape space:SP -E star:STAR --esc at:AT --ESCAPE quest:Q
    ...    --name STARSPnameSPSTAR --doc ATAT --include pQQs
    Run Rebot    ${opts}    ${INPUT FILE}
