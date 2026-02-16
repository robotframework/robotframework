*** Settings ***
Suite Teardown    Remove Items
Test Setup        Remove Items
Library           OperatingSystem
Library           ./wait_until_library.py

*** Variables ***
${FILE}              %{TEMPDIR}${/}ROBOTEST-F.txt
${FILE 2}            %{TEMPDIR}${/}ROBOTEST-F-2.txt
${DIR}               %{TEMPDIR}${/}ROBOTEST-D
${FILE PATTERN}      %{TEMPDIR}${/}ROBOTEST-*.txt
${DIR PATTERN}       %{TEMPDIR}${/}ROBOTEST-?
${BOTH PATTERN}      %{TEMPDIR}${/}ROBOTEST-*
${FILE WITH GLOB}    %{TEMPDIR}${/}ROBOTEST[glob].txt

*** Test Cases ***
Wait removal when do not exist
    Wait Until Removed       ${FILE}
    Wait Until Removed       ${DIR}

Removed before timeout
    Create Items
    Remove After Sleeping    ${FILE}
    Wait Until Removed       ${FILE}    5 second
    Remove After Sleeping    ${DIR}
    Wait Until Removed       ${DIR}    32 seconds 44 millis

Removed before timeout when using glob pattern
    Create Items
    Remove After Sleeping    ${FILE}    ${FILE 2}
    Wait Until Removed       ${FILE PATTERN}    23
    Remove After Sleeping    ${DIR}
    Wait Until Removed       ${DIR PATTERN}    12 s
    Create Items
    Remove After Sleeping    ${FILE}    ${FILE 2}    ${DIR}
    Wait Until Removed       ${BOTH PATTERN}

File not removed before timeout
    [Documentation]    FAIL '${FILE}' was not removed in 50 milliseconds.
    Create Items
    Wait Until Removed       ${FILE}    0.05

Directory not removed before timeout
    [Documentation]    FAIL '${DIR}' was not removed in 50 milliseconds.
    Create Items
    Wait Until Removed       ${DIR}    0 days 0 hours 50 milliseconds

Not removed before timeout when using glob pattern
    [Documentation]    FAIL '${BOTH PATTERN}' was not removed in 42 milliseconds.
    Create Items
    Wait Until Removed       ${BOTH PATTERN}    0.042

Wait removal when path itself contains glob charactes
    [Documentation]    FAIL '${FILE WITH GLOB}' was not removed in 42 milliseconds.
    Wait Until Removed       ${FILE WITH GLOB}    1 hour
    Create File              ${FILE WITH GLOB}
    Remove After Sleeping    ${FILE WITH GLOB}
    Wait Until Removed       ${FILE WITH GLOB}    1 day
    Create File              ${FILE WITH GLOB}
    Wait Until Removed       ${FILE WITH GLOB}    0.042

Wait removal when using `pathlib.Path`
    [Documentation]    FAIL '${FILE}' was not removed in 42 milliseconds.
    VAR                      ${PATH}    ${{pathlib.Path($FILE)}}
    Wait Until Removed       ${PATH}    1 hour
    Create File              ${PATH}
    Remove After Sleeping    ${PATH}
    Wait Until Removed       ${PATH}    1 day
    Create File              ${PATH}
    Wait Until Removed       ${PATH}    0.042

None disables remove timeout
    [Documentation]    In practice this only validates that None is accepted.
    ...                Waiting until the default timeout exceeds would take too much time.
    ...                FAIL    Test timeout 100 milliseconds exceeded.
    [Timeout]          0.1 s
    Create File              ${FILE}
    Wait Until Removed       ${FILE}    timeout=None

Invalid remove timeout
    [Documentation]    FAIL ValueError: Argument 'timeout' got value 'invalid' that cannot be converted to timedelta or None.
    Wait Until Removed       non-existing    invalid

Wait creation when already created
    Create Items
    Wait Until Created       ${FILE}
    Wait Until Created       ${DIR}

Created before timeout
    Create After Sleeping    ${FILE}
    Wait Until Created       ${FILE}    1111 ms
    Create After Sleeping    ${DIR}     directory=True
    Wait Until Created       ${DIR}     1.111 seconds

Created before timeout when using glob pattern
    Create After Sleeping    ${FILE}
    Wait Until Created       ${FILE PATTERN}
    Create After Sleeping    ${DIR}     directory=True
    Wait Until Created       ${DIR PATTERN}

File not created before timeout
    [Documentation]    FAIL '${FILE}' was not created in 23 milliseconds.
    Wait Until Created       ${FILE}    0.023

Directory not created before timeout
    [Documentation]    FAIL '${DIR}' was not created in 42 milliseconds.
    Wait Until Created       ${DIR}     0 s 42 ms

Not created before timeout when using glob pattern
    [Documentation]    FAIL '${BOTH PATTERN}' was not created in 22 milliseconds.
    Wait Until Created       ${BOTH PATTERN}    0.022

Wait creation when path itself contains glob charactes
    [Documentation]    FAIL '${FILE WITH GLOB}' was not created in 42 milliseconds.
    Create After Sleeping    ${FILE WITH GLOB}
    Wait Until Created       ${FILE WITH GLOB}    1 hour
    Remove File              ${FILE WITH GLOB}
    Wait Until Created       ${FILE WITH GLOB}    0.042

Wait creation when using `pathlib.Path`
    [Documentation]    FAIL '${FILE}' was not created in 42 milliseconds.
    VAR                      ${PATH}    ${{pathlib.Path($FILE)}}
    Create After Sleeping    ${PATH}
    Wait Until Created       ${PATH}    1 hour
    Remove File              ${PATH}
    Wait Until Created       ${PATH}    0.042

None disables create timeout
    [Documentation]    In practice this only validates that None is accepted.
    ...                Waiting until the default timeout exceeds would take too much time.
    ...                FAIL    Test timeout 100 milliseconds exceeded.
    [Timeout]          0.1 s
    Wait Until Created       ${FILE}    timeout=None

Invalid create timeout
    [Documentation]    FAIL ValueError: Argument 'timeout' got value 'invalid' that cannot be converted to timedelta or None.
    Wait Until Created       ${CURDIR}    invalid

*** Keywords ***
Remove Items
    Remove File         ${FILE WITH GLOB}
    Remove File         ${FILE}
    Remove File         ${FILE 2}
    Remove Directory    ${DIR}

Create Items
    Create File         ${FILE WITH GLOB}
    Create File         ${FILE}
    Create File         ${FILE 2}
    Create Directory    ${DIR}
