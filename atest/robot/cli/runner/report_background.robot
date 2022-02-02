*** Settings ***
Resource        cli_resource.robot

*** Test Cases ***
Default colors
    [Template]  Report should have correct background
    ${EMPTY}

Two custom colors
    [Template]  Report should have correct background
    --reportbackground blue:red  blue  red

Three custom colors
    [Template]  Report should have correct background
    --reportback green:red:yellow  green  red  yellow

Invalid Colors
    Run Should Fail    --reportback invalid ${SUITE_SOURCE}
    ...    Invalid value for option '--reportbackground': Expected format 'pass:fail:skip' or 'pass:fail', got 'invalid'.

*** Keywords ***
Report should have correct background
    [Arguments]  ${opt}  ${pass}=#9e9  ${fail}=#f66  ${skip}=#fed84f
    Run Tests  ${opt} --report rep.html  misc/pass_and_fail.robot
    ${report} =  Get File  ${OUTDIR}/rep.html
    Should Contain  ${report}  "background":{"fail":"${fail}","pass":"${pass}","skip":"${skip}"},
