*** Settings ***
Documentation   Verify that stat information is written correctly to log/report
Resource        atest_resource.robot
Library         html_output_stats.py
Suite Setup     Run tests with stat related options

*** Test Cases ***
Log contains total stats
    Verify total stats    log.html

Report contains total stats
    Verify total stats    report.html

Log contains tag stats
    Verify tag stats    log.html

Report contains tag stats
    Verify tag stats    report.html

Log contains suite stats
    Verify suite stats    log.html

Report contains suite stats
    Verify suite stats    report.html


*** Keywords ***
Run tests with stat related options
    ${opts} =    Catenate
    ...    --Critical t1
    ...    --NonCritical t2
    ...    --SuiteStatLevel 2
    ...    --TagStatInclude t?
    ...    --TagStatInclude d1
    ...    --TagStatCombine f1ANDt1
    ...    --TagDoc "t1:the doc"
    ...    --TagStatLink t?:http://t/%1:T%1
    ...    --log log.html
    ...    --report report.html
   Run tests    ${opts}    misc/suites

Verify total stats
    [Arguments]    ${file}
    ${critical}    ${all} =    Get Total Stats    ${OUTDIR}${/}${file}
    Verify stat    ${critical}    label:Critical Tests    pass:5    fail:1
    Verify stat    ${all}    label:All Tests    pass:10    fail:1

Verify tag stats
    [Arguments]    ${file}
    ${stats} =    Get Tag Stats    ${OUTDIR}${/}${file}
    Length Should Be    ${stats}    4
    Verify stat    ${stats[0]}    label:t1    pass:5    fail:1
    ...    info:critical    links:T1:http://t/1    doc:the doc
    Verify stat    ${stats[1]}    label:t2    pass:2    fail:0
    ...    info:non-critical    links:T2:http://t/2
    Verify stat    ${stats[2]}    label:f1 AND t1    pass:5    fail:1
    ...    info:combined    combined:f1 AND t1
    Verify stat    ${stats[3]}    label:d1    pass:1    fail:0

Verify suite stats
    [Arguments]    ${file}
    ${stats} =    Get Suite Stats    ${OUTDIR}${/}${file}
    Length Should Be    ${stats}    7
    Verify stat    ${stats[0]}    label:Suites    name:Suites
    ...    id:s1    pass:10    fail:1
    Verify stat    ${stats[1]}    label:Suites.Fourth    name:Fourth
    ...    id:s1-s1    pass:0    fail:1
    Verify stat    ${stats[2]}    label:Suites.Subsuites    name:Subsuites
    ...    id:s1-s2    pass:2    fail:0
    Verify stat    ${stats[3]}    label:Suites.Subsuites2    name:Subsuites2
    ...    id:s1-s3    pass:3    fail:0
    Verify stat    ${stats[4]}    label:Suites.Tsuite1    name:Tsuite1
    ...    id:s1-s4    pass:3    fail:0
    Verify stat    ${stats[5]}    label:Suites.Tsuite2    name:Tsuite2
    ...    id:s1-s5    pass:1    fail:0
    Verify stat    ${stats[6]}    label:Suites.Tsuite3    name:Tsuite3
    ...    id:s1-s6    pass:1    fail:0
