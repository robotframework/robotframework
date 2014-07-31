*** Settings ***
Resource        atest_resource.txt
Force Tags      regression  pybot  jybot
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
    Run Tests  ${options} -r pybotreport.html   misc/pass_and_fail.txt
    Copy File   ${OUTDIR}${/}pybotreport.html   %{TEMPDIR}${/}pybotreport.html
    Run Rebot  -r rebotreport.html ${options}   ${OUTFILE}
    Copy File   ${OUTDIR}${/}rebotreport.html   %{TEMPDIR}${/}rebotreport.html
    Difference between stuff   %{TEMPDIR}${/}pybotreport.html   %{TEMPDIR}${/}rebotreport.html
    [Teardown]   Remove Files    %{TEMPDIR}${/}pybotreport.html   %{TEMPDIR}${/}rebotreport.html



