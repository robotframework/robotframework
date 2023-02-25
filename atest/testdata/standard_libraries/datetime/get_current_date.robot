*** Settings ***
Library           DateTime
Variables         datesandtimes.py

*** Test Cases ***
Local time
    ${start} =    Evaluate    datetime.datetime.now()    modules=datetime
    Sleep    0.01s
    ${date1} =    Get Current Date    result_format=datetime
    Sleep    0.01s
    ${date2} =    Get Current Date    local    result_format=datetime
    Sleep    0.01s
    ${end} =    Evaluate    datetime.datetime.now()    modules=datetime
    Compare Datatimes    ${start}    ${date1}     difference=0.01
    Compare Datatimes    ${date1}    ${date2}     difference=0.01
    Compare Datatimes    ${date2}    ${end}       difference=0.01

UTC Time
    ${utc1} =    Get Current Date    UTC    result_format=datetime
    Sleep    0.01s
    ${utc2} =    Get Current Date    utc    result_format=datetime
    ${local} =    Get Current Date    result_format=datetime
    Compare Datatimes    ${utc1}    ${utc2}     difference=0.01
    Compare Datatimes    ${utc2}    ${local}    difference=-${TIMEZONE}

Invalid time zone
    [Documentation]    FAIL ValueError: Unsupported timezone 'invalid'.
    Get Current Date    invalid

Increment
    ${date1} =    Get Current Date    result_format=datetime
    ${date2} =    Get Current Date    increment=2h    result_format=datetime
    Compare Datatimes    ${date1}    ${date2}    difference=hours=2

Negative Increment
    ${date1} =    Get Current Date    result_format=datetime
    ${date2} =    Get Current Date    local    -3 minutes    datetime
    Compare Datatimes    ${date1}    ${date2}    difference=minutes=-3

Default result format
    ${date} =    Get Current Date
    Should Match Regexp    ${date}    ^20\\d{2}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}.\\d{3}$

Result format timestamp
    ${date} =    Get Current Date    result_format=timestamp
    Should Match Regexp    ${date}    ^20\\d{2}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}.\\d{3}$
    ${date} =    Get Current Date    result_format=timestamp    exclude_millis=True
    Should Match Regexp    ${date}    ^20\\d{2}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}$

Result format custom timestamp
    ${date} =    Get Current Date    result_format=%d.%m.%Y
    Should Match Regexp    ${date}    ^\\d{2}\\.\\d{2}\\.20\\d{2}$

Result format epoch
    ${result} =    Get Current Date    result_format=epoch
    # Round `time.time()` to same precision as `datetime` that `Get Current Date` uses.
    Should Be True    0 <= round(time.time(), 6) - ${result} < 1

Local and UTC epoch times are same
    ${local} =    Get Current Date    local    result_format=epoch
    ${utc} =      Get Current Date    utc      result_format=epoch
    Should Be True    0 <= ${utc} - ${local} < 1

Result format datetime
    ${start} =    Evaluate    datetime.datetime.now()    modules=datetime
    ${dt} =    Get Current Date    result_format=datetime
    ${end} =    Evaluate    datetime.datetime.now()    modules=datetime
    Compare Datatimes    ${start}    ${dt}
    Compare Datatimes    ${dt}    ${end}

*** Keywords ***
Compare Datatimes
    [Arguments]    ${dt1}    ${dt2}    ${difference}=0
    ${result} =    Evaluate    $dt2 - $dt1 - datetime.timedelta(0, ${difference})
    Should Be True    0 <= ${result.total_seconds()} < 1
