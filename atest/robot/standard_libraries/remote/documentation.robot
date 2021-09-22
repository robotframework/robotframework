*** Settings ***
Suite Setup      Run Remote Tests And Libdoc
Resource         remote_resource.robot
Test Template    Verify executed short doc and full Libdoc

*** Test Cases ***
Empty
    ${EMPTY}    ${EMPTY}    0

Single
    Single line documentation    Single line documentation    3

Multi
    Short doc\nin two lines.    Short doc\nin two lines.\n\nDoc body\nin\nthree.    1

Nön-ÄSCII
    Nön-ÄSCII documentation    Nön-ÄSCII documentation    2

Intro documentation
    [Template]    Doc Should Be
    Remote library for documentation testing purposes

Init documentation
    [Template]    Init Doc Should Start With
    0    Connects to a remote server at ``uri``.

Keyword arguments
    [Template]    Keyword Arguments Should Be
    0
    3    arg
    1    a1    a2=d    *varargs

Init arguments
    [Template]    Init Arguments Should Be
    0    uri=http://127.0.0.1:8270    timeout=None

*** Keywords ***
Run Remote Tests And Libdoc
    ${port} =    Run Remote Tests    documentation.robot    documentation.py    stop server=no
    Run Libdoc And Parse Output    Remote::http://127.0.0.1:${port}
    [Teardown]      Run Keywords
    ...    Stop Remote Server    documentation.py    AND
    ...    Remove Output Files

Verify executed short doc and full Libdoc
    [Arguments]    ${short}    ${full}    ${index}
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].doc}    ${short}
    Keyword Name Should Be    ${index}    ${TEST NAME}
    Keyword Doc Should Be     ${index}    ${full}
