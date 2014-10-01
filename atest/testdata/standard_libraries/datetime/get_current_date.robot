*** Settings ***
Library          DateTime
Variables        datesandtimes.py

*** Test Cases ***
Local time increases
    ${date1} =  Get Current Date  result_format=epoch
    ${date2} =  Get Current Date  increment=1s  result_format=epoch
    Should Be True  ${date2} > ${date1}

UTC Time
    ${before} =   Get Current Date  result_format=epoch
    ${utc} =      Get Current Date  UTC  result_format=epoch
    ${after} =    Get Current Date  result_format=epoch
    Should Be True  ${before} <= ${utc} - ${TIMEZONE} <= ${after}

Invalid time zone
    [Documentation]    FAIL ValueError: Unsupported timezone 'invalid'.
    Get Current Date    invalid

Increment
    ${date1} =  Get Current Date  result_format=epoch
    ${date2} =  Get Current Date  increment=2h  result_format=epoch
    Should Be True  7201 >= ${date2} - ${date1} >= 7200

Negative Increment
    ${date1} =  Get Current Date  result_format=epoch
    ${date2} =  Get Current Date  increment=-3minutes  result_format=epoch
    Should Be True  -179 >= ${date2} - ${date1} >= -180

Result format timestamp
    ${date} =  Get Current Date   result_format=timestamp
    Should Match Regexp  ${date}  \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}

Result format epoch
    ${date} =  Get Current Date   result_format=epoch
    Should Be True  1000000000 < ${date} < 2000000000

Result format datetime
    ${before} =  Evaluate  datetime.datetime.now().isoformat()  datetime
    ${dt} =  Get Current Date   result_format=datetime
    ${after} =  Evaluate  datetime.datetime.now().isoformat()  datetime
    Should Be True  "${before}" <= "${dt.isoformat()}" <= "${after}"
