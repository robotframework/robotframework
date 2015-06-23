*** Settings ***
Test Template     Time conversion should succeed
Library           DateTime
Variables         datesandtimes.py

*** Test Cases ***    INPUT              FORMAT       EXPECTED
Convert to number     10 s               number       ${10}
                      ${-62.3}           NUMBER       ${-62.3}
                      ${0.123456789}     number       ${0.123456789}
                      ${timedelta(2)}    NUMber       ${172800}

Convert to string     10 s               verbose      10 seconds
                      ${-62.3}           VERBOSE      - 1 minute 2 seconds 300 milliseconds
                      ${0.123456789}     verbose      123 milliseconds
                      ${0.1239}          verbose      124 milliseconds
                      ${timedelta(2)}    VERbose      2 days

Convert to compact string
                      10 s               compact      10s
                      ${-62.3}           COMPACT      - 1min 2s 300ms
                      ${0.123456789}     compact      123ms
                      ${timedelta(2)}    COMpact      2d

Convert to timer      10 s               timer        00:00:10.000
                      ${-62.3}           TIMER        -00:01:02.300
                      ${0.123456789}     timer        00:00:00.123
                      ${timedelta(5)}    TImeR        120:00:00.000

Convert to timedelta
                      10 s               timedelta    ${timedelta(seconds=10)}
                      ${-62.3}           TIMEDELTA    ${timedelta(minutes=-1, seconds=-2.3)}
                      ${0.123456789}     timedelta    ${timedelta(microseconds=123457)}
                      ${timedelta(2)}    TIMEdelta    ${timedelta(2)}

Ignore millis         [Template]         Time conversion without millis should succeed
                      61.5               number       ${62}
                      61.5               verbose      1 minute 2 seconds
                      61.5               compact      1min 2s
                      61.5               timer        00:01:02
                      61.5               timedelta    ${timedelta(seconds=62)}

Number is float regardless are millis included or not
                      [Template]    Number format should be
                      ${1000.123}        1000.123     no
                      ${1000}            1000.0       ${0}
                      ${1000.123}        1000.0       ${1}
                      ${1000}            1000.0       no millis

Invalid format        [Documentation]    FAIL ValueError: Unknown format 'invalid'.
                      10s                invalid      0

*** Keywords ***
Time conversion should succeed
    [Arguments]    ${input}    ${format}    ${expected}
    ${result} =    Convert Time    ${input}    ${format}
    Should Be Equal    ${result}    ${expected}

Time conversion without millis should succeed
    [Arguments]    ${input}    ${format}    ${expected}
    ${result} =    Convert Time    ${input}    ${format}    exclude_millis=Yes
    Should Be Equal    ${result}    ${expected}

Number format should be
    [Arguments]    ${input}    ${expected}    ${millis}
    ${result} =    Convert Time    ${input}    result_format=number    exclude_millis=${millis}
    Should Be Equal As Strings    ${result}    ${expected}
