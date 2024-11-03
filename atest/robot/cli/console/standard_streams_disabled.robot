*** Settings ***
Suite Setup       Run tests with standard streams disabled
Resource          console_resource.robot

*** Test Cases ***
Execution succeeds
    Should Be Equal    ${SUITE.name}    Log

Console outputs are disabled
    Stdout Should Be    empty.txt
    Stderr Should Be    empty.txt

Log To Console keyword succeeds
    Check Test Case    Log to console

*** Keywords ***
Run tests with standard streams disabled
    [Documentation]    Streams are disabled by using the sitecustomize module:
    ...                https://docs.python.org/3/library/site.html#module-sitecustomize
    Copy File    ${CURDIR}/disable_standard_streams.py    %{TEMPDIR}/sitecustomize.py
    Set Environment Variable    PYTHONPATH    %{TEMPDIR}
    Run Tests   ${EMPTY}    standard_libraries/builtin/log.robot
    [Teardown]    Remove File    %{TEMPDIR}/sitecustomize.py
