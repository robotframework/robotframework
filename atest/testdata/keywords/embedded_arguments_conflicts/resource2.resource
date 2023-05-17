*** Keywords ***
${match} in ${both} resources
    Should be equal    ${match}    Match
    Should be equal    ${both}     both

${match} resources
    Fail    Should not be run due to being worse match than above

Follow search ${order} in resources
    Should be equal    ${order}    order

Unresolvable ${conflict} in resource
    Fail    Should not be run due to conflict

${possible} conflict in resource
    Should be equal    ${possible}    No

Better ${private} match
    [Tags]    robot:private
    Fail    Should not be run due to being private in different file

Another ${match} in both resource files
    Fail    Better match but should not be run due to being in different file

Match ${with and without} embedded arguments in different files
    Should be equal    ${with and without}    with
