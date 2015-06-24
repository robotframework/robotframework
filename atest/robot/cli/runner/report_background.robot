*** Settings ***
Force Tags      regression  pybot  jybot
Resource        cli_resource.robot

*** Test Cases ***
Default colors
    [Template]  Report should have correct background
    ${EMPTY}

Two custom colors
    [Template]  Report should have correct background
    --reportbackground blue:red  blue  blue  red

Three custom colors
    [Template]  Report should have correct background
    --reportback green:yellow:red  green  yellow  red

Invalid Colors
    Run Should Fail  --reportback invalid ${SUITE_SOURCE}
    ...  Invalid report background colors 'invalid'.

*** Keywords ***
Report should have correct background
    [Arguments]  ${opt}  ${pass}=#9e9  ${noncrit}=#9e9  ${fail}=#f66
    Run Tests  ${opt} --report rep.html  misc/pass_and_fail.robot
    ${report} =  Get File  ${OUTDIR}/rep.html
    Should Contain  ${report}  "background":{"fail":"${fail}","nonCriticalFail":"${noncrit}","pass":"${pass}"},
