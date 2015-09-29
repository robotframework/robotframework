*** Settings ***
Resource        atest_resource.robot
Library         nolog.py
Test Template   Run With Options

*** Test Cases ***
Should be same
    -l none --tagstatcombine passANDfail
    --tagstatcombine passANDfail
    -l none --tagstatexclude pass
    -l none --tagstatinclude pass

*** Keywords ***
Run With Options  [Arguments]   ${options}
    Run Tests  ${options} -r %{TEMPDIR}/robot-report.html   misc/pass_and_fail.robot
    Copy Previous Outfile
    Run Rebot  -r %{TEMPDIR}/rebot-report.html ${options}   ${OUTFILE COPY}
    Reports should be equal   %{TEMPDIR}/robot-report.html   %{TEMPDIR}/rebot-report.html
