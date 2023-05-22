*** Settings ***
Resource          embedded_arguments_conflicts/resource.resource
Resource          embedded_arguments_conflicts/resource2.resource
Library           embedded_arguments_conflicts/library.py
Library           embedded_arguments_conflicts/library2.py

*** Variables ***
${INDENT}         ${SPACE * 4}

*** Test Cases ***
Unique match in suite file
    Execute "robot"
    Automation framework
    Robot uprising

Best match wins in suite file
    Execute "x" on device "y"

Conflict in suite file 1
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'Execute "ls"' found:
    ...    ${INDENT}Execute "\${command:(ls|grep)}"
    ...    ${INDENT}Execute "\${command}"
    Execute "ls"

Conflict in suite file 2
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'Robot Framework' found:
    ...    ${INDENT}\${x} Framework
    ...    ${INDENT}Robot \${x}
    Robot Framework

Unique match in resource
    x in resource
    No conflict in resource

Best match wins in resource
    x and y in resource

Conflict in resource
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'y in resource' found:
    ...    ${INDENT}resource.\${x} in resource
    ...    ${INDENT}resource.\${y:y} in resource
    y in resource

Unique match in resource with explicit usage
    resource.x in resource
    resource2.No conflict in resource

Best match wins in resource with explicit usage
    resource.x and y in resource

Conflict in resource with explicit usage
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'resource.y in resource' found:
    ...    ${INDENT}resource.\${x} in resource
    ...    ${INDENT}resource.\${y:y} in resource
    resource.y in resource

Unique match in library
    x in library
    No conflict in library

Best match wins in library
    x and y in library

Conflict in library
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'y in library' found:
    ...    ${INDENT}library.\${x} in library
    ...    ${INDENT}library.\${y:y} in library
    y in library

Unique match in library with explicit usage
    library.x in library
    library2.No conflict in library

Best match wins in library with explicit usage
    library.x and y in library

Conflict in library with explicit usage
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'library.y in library' found:
    ...    ${INDENT}library.\${x} in library
    ...    ${INDENT}library.\${y:y} in library
    library.y in library

Search order resolves conflict with resources
    [Setup]    Enable search order
    Match in both resources
    [Teardown]    Disable search order

Search order wins over best match in resource
    [Setup]    Enable search order
    Follow search order in resources
    [Teardown]    Disable search order

Search order resolves conflict with libraries
    [Setup]    Enable search order
    Match in both libraries
    [Teardown]    Disable search order

Search order wins over best match in libraries
    [Setup]    Enable search order
    Follow search order in libraries
    [Teardown]    Disable search order

Search order cannot resolve conflict within resource
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'Unresolvable conflict in resource' found:
    ...    ${INDENT}resource2.\${possible} conflict in resource
    ...    ${INDENT}resource2.Unresolvable \${conflict} in resource
    [Setup]    Enable search order
    Unresolvable conflict in resource
    [Teardown]    Disable search order

Search order causes conflict within resource
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'Unresolvable conflict in resource' found:
    ...    ${INDENT}resource2.\${possible} conflict in resource
    ...    ${INDENT}resource2.Unresolvable \${conflict} in resource
    [Setup]    Enable search order
    Cause unresolvable conflict in resource due to search order
    [Teardown]    Disable search order

Search order cannot resolve conflict within library
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'Unresolvable conflict in library' found:
    ...    ${INDENT}library2.\${possible} conflict in library
    ...    ${INDENT}library2.Unresolvable \${conflict} in library
    [Setup]    Enable search order
    Unresolvable conflict in library
    [Teardown]    Disable search order

Search order causes conflict within library
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'Unresolvable conflict in library' found:
    ...    ${INDENT}library2.\${possible} conflict in library
    ...    ${INDENT}library2.Unresolvable \${conflict} in library
    [Setup]    Enable search order
    Cause unresolvable conflict in library due to search order
    [Teardown]    Disable search order

Public match wins over better private match in different resource
    [Documentation]    and better match wins when both are in same file
    Better public match

Match in same resource wins over better match elsewhere
    [Documentation]    even if match in same file would be private
    Match in same resource wins over better match elsewhere

Keyword without embedded arguments wins over keyword with them in same file
    Match with and without embedded arguments
    Match with embedded arguments

Keyword without embedded arguments wins over keyword with them in different file
    Match with and without embedded arguments in different files
    Match with embedded arguments in different files

*** Keywords ***
Execute "${command}"
    Should be equal    ${command}    robot

Execute "${command}" on device "${device}"
    Should be equal    ${command}    x
    Should be equal    ${device}    y

Execute "${command:(ls|grep)}"
    Fail    Should not be run due to conflict

${x} Framework
    Should be equal    ${x}    Automation

Robot ${x}
    Should be equal    ${x}    uprising

Match with and without embedded arguments
    No Operation

Match ${with and without} embedded arguments
    Should be equal    ${with and without}    with

Enable search order
    Set library search order    resource2    library2

Disable search order
    Set library search order
