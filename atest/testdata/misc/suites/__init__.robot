*** Settings ***
Suite Setup       ${SUITE_SETUP}
Suite Teardown    ${SUITE_TEARDOWN}    ${SUITE_TEARDOWN_ARG}
Library           OperatingSystem

*** Variables ***
${SUITE_SETUP}           NONE
${SUITE_TEARDOWN}        Log
${SUITE_TEARDOWN_ARG}    Default suite teardown
