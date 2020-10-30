*** Variables ***
${scalar}=    Some Test


*** Keywords ***
Check Scalar in Default
    [Arguments]
    ...     ${current}=some\${text} and ${scalar} \ ${{'Hello'[1:3]}}\ with\n\t space
    ...    ${expected}=some\${text} and ${scalar} \ ${{'Hello'[1:3]}}\ with\n\t space
    Log    current: '${current}'
    Log    expected: '${expected}'
    Should Be Equal    ${current}    ${expected}
