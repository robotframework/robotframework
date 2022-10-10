*** Settings ***
Test Template     Time conversion should succeed
Library           DateTime
Variables         datesandtimes.py

*** Test Cases ***    INPUT                                 EXPECTED
Time string           10 s                                  10
                      0.5 seconds                           0.5
                      1d 2h 3m 4s 5ms                       93784.005
                      1 day 2 hours 3 min 4 sec 5 millis    93784.005
                      999.9 milliseconds                    0.9999
                      -10s                                  -10
                      - 1 min 0.5 sec                       -60.5
                      0 days 2 mins 0 s                     120
                      0 s                                   0
                      0.1 millisecond                       0.0001
                      0.123456789 ms                        0.000123456789
                      123 μs                                0.000123
                      1 ns                                  1E-9

Number as string      10                                    10
                      0.5                                   0.5
                      -1                                    -1
                      0                                     0
                      0.123456789                           0.123456789
                      1E-9                                  1E-9

Number                ${42}                                 42
                      ${3.14}                               3.14
                      ${-0.5}                               -0.5
                      ${0}                                  0
                      ${0.123456789}                        0.123456789
                      ${1E-9}                               1E-9

Timer                 00:00:00.000                          0
                      00:00:00.001                          0.001
                      00:00:01.000                          1
                      00:00:01.5                            1.5
                      01:02:03.004                          3723.004
                      99:59:59.999                          359999.999
                      100:00:00.000                         360000
                      -01:02:03.004                         -3723.004
                      +01:02:03.004                         3723.004
                      0:00:00.001                           0.001
                      1:00:00.000                           3600
                      000000000:00:00.001                   0.001
                      000000001:00:00.000                   3600
                      000000001:00:00.5000000               3600.5
                      000000001:00:00.5                     3600.5
                      1:2:3                                 3723
                      00:00.123456789                       0.123456789

Timer without millis
                      00:00:00                              0
                      00:00:01                              1
                      01:02:03                              3723
                      99:59:59                              359999
                      100:00:00                             360000

Timer without hours
                      00:00                                 0
                      01:02                                 62
                      0:0                                   0
                      1:2                                   62
                      00:00.123                             0.123
                      000:000.000                           0
                      007:007.007                           427.007
                      0:0.0                                 0
                      1:2.3                                 62.3

Timedelta             ${timedelta(1)}                       86400
                      ${timedelta(seconds=1.5)}             1.5
                      ${timedelta(hours=-1)}                -3600
                      ${timedelta(microseconds=1234567)}    1.234567

Invalid               [Template]    Time conversion should fail
                      kekkonen
                      1 foo
                      01:02:03:04
                      01:02foo

*** Keywords ***
Time conversion should succeed
    [Arguments]    ${input}    ${expected}
    ${expected} =    Convert To Number    ${expected}
    ${result} =    Convert Time    ${input}
    Should Be Equal    ${result}    ${expected}

Time conversion should fail
    [Arguments]    ${input}
    Run Keyword And Expect Error
    ...    ValueError: Invalid time string '${input}'.
    ...    Convert Time    ${input}
