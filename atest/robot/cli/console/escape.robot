*** Settings ***
Suite Setup       Run tests with escaping
Resource          console_resource.robot

*** Test Cases ***
--escape options and arguments
    Should be equal    ${SUITE.name}    * name *
    Should be equal    ${SUITE.doc}    @@
    Should contain tests    ${SUITE}    Pass

--escape is deprecated
    Check log message    ${ERRORS[0]}    Option '--escape' is deprecated. Use console escape mechanism instead.    WARN
    Stderr Should Be Equal To    [ WARN ] Option '--escape' is deprecated. Use console escape mechanism instead.\n

*** Keywords ***
Run tests with escaping
    ${opts} =    Catenate
    ...    --escape space:SP -E star:STAR --esc at:AT --ESCAPE quest:Q
    ...    --name STARSPnameSPSTAR --doc ATAT --include pQQs
    Run tests    ${opts}    misc/pass_and_fail.robot
