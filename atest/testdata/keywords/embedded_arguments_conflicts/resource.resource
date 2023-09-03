*** Keywords ***
${x} in resource
    Should be equal    ${x}    x

${x} and ${y} in resource
    Should be equal    ${x}    x
    Should be equal    ${y}    y

${y:y} in resource
    Fail    Should not be run due to conflict

${match} in ${both} resources
    Fail    Should not be run due to search order

Follow search ${disorder} in resources
    Fail    Should not be run due to search order

${public} match
    Should be equal    ${public}    Better public
    Better private match

Better ${private} match
    [Tags]    robot:private
    Should be equal    ${private}    private

Match in same resource wins over better match elsewhere
    Another match in both resource files

Another match ${in both resource files}
    [Tags]    robot:private
    Should be equal    ${in both resource files}    in both resource files

Match with and without embedded arguments in different files
    No operation

Cause unresolvable conflict in resource due to search order
    Unresolvable conflict in resource

Cause unresolvable conflict in library due to search order
    Unresolvable conflict in library

Unresolvable conflict in resource
    Fail    Should not be run due to search order
