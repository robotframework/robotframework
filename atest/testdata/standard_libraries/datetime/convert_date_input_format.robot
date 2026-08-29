*** Settings ***
Test Template     Date Conversion Should Succeed
Library           DateTime
Variables         datesandtimes.py

*** Test Cases ***    INPUT                                           OUTPUT                           CONFIG
Timestamp             2014-04-24 21:45:12.123                         2014-04-24 21:45:12.123
                      2014-04-24 21:45:12                             2014-04-24 21:45:12.000
                      2014-04-24T21:45:12.123                         2014-04-24 21:45:12.123
                      2014.04+24@@21/45!12,123                        2014-04-24 21:45:12.123
                      2014foo06bar05                                  2014-06-05 00:00:00.000

Custom timestamp      2014-04-24 21:45:12.123                         2014-04-24 21:45:12.123          %Y-%m-%d %H:%M:%S.%f
                      2014-04-24T21:45:12.123                         2014-04-24 21:45:12.123          %Y-%m-%dT%H:%M:%S.%f
                      24.4.2014 21:45:12-123                          2014-04-24 21:45:12.123          %d.%m.%Y %H:%M:%S-%f
                      04/24/2014T21.45.12                             2014-04-24 21:45:12.000          %m/%d/%YT%H.%M.%S
                      24.04.2014                                      2014-04-24 00:00:00.000          %d.%m.%Y
                      24-04.2014@21                                   2014-04-24 21:00:00.000          %d-%m.%Y@%H
                      21:45:12.123 24.04.2014                         2014-04-24 21:45:12.123          %H:%M:%S.%f %d.%m.%Y

TODAY and NOW         [Template]    Date Conversion Should Yield Current Date
                      TODAY
                      now

Epoch                 ${EPOCH}                                        2018-11-22 13:13:42.000
                      ${EPOCH + 0.123}                                2018-11-22 13:13:42.123
                      ${EPOCH + 0.5}                                  2018-11-22 13:13:42.500
                      ${BIG EPOCH}                                    2160-02-18 10:40:00.000

Datetime object       ${datetime(2014, 4, 24, 21, 45, 12, 123000)}    2014-04-24 21:45:12.123
                      ${datetime(2014, 4, 24, 21, 45, 12, 123456)}    2014-04-24 21:45:12.123
                      ${datetime(2014, 4, 24, 21, 45, 12, 123500)}    2014-04-24 21:45:12.124
                      ${datetime(2014, 4, 24, 21)}                    2014-04-24 21:00:00.000

Date object           ${date(2023, 12, 18)}                           2023-12-18 00:00:00.000

Pad zeroes to missing values
                      2014-04-24                                      2014-04-24 00:00:00.000
                      2014.04.24 21                                   2014-04-24 21:00:00.000

Rounding milliseconds
                      2014-04-24 21:45:12.123456                      2014-04-24 21:45:12.123
                      2014-04-24 21:45:12.1234                        2014-04-24 21:45:12.123
                      2014-04-24 21:45:12.1235                        2014-04-24 21:45:12.124
                      2014-04-24T21:45:12.123456                      2014-04-24 21:45:12.123          %Y-%m-%dT%H:%M:%S.%f
                      2014-04-24T21:45:12.1234                        2014-04-24 21:45:12.123          %Y-%m-%dT%H:%M:%S.%f
                      2014-04-24T21:45:12.1235                        2014-04-24 21:45:12.124          %Y-%m-%dT%H:%M:%S.%f
                      ${EPOCH + 0.123456}                             2018-11-22 13:13:42.123
                      ${EPOCH + 0.1234}                               2018-11-22 13:13:42.123
                      ${EPOCH + 0.5}                                  2018-11-22 13:13:43              exclude_millis=True
                      ${EPOCH - 0.5}                                  2018-11-22 13:13:42              exclude_millis=True
                      ${datetime(2014, 4, 24, 21, 45, 12, 123456)}    2014-04-24 21:45:12.123
                      ${datetime(2014, 4, 24, 21, 45, 12, 123400)}    2014-04-24 21:45:12.123
                      ${datetime(2014, 4, 24, 21, 45, 12, 123500)}    2014-04-24 21:45:12.124

Invalid input        [Template]    Date Conversion Should Fail
                     bad                                              Invalid timestamp 'bad'.
                     2014-06                                          Invalid timestamp '2014-06'.
                     2014-6-5                                         Invalid timestamp '2014-6-5'.
                     2014-06-05                                       *                                %Y-%m-%d %H:%M:%S.%f
                     2015-xxx                                         *                                %Y-%f
                     ${NONE}                                          Invalid timestamp 'None'.

*** Keywords ***
Date Conversion Should Succeed
    [Arguments]    ${input}    ${expected}    ${input_format}=${NONE}    &{config}
    ${date} =    Convert Date    ${input}    date_format=${input_format}    &{config}
    Should Be Equal    ${date}    ${expected}

Date Conversion Should Yield Current Date
    [Arguments]    ${input}
    ${date} =    Convert Date    ${input}    result_format=datetime
    ${delta} =    Subtract Date From Date    ${datetime.now()}    ${date}
    Should Be True    ${delta} < 0.1
    ${date} =    Convert Date    ${input}    result_format=date
    Should Be Equal    ${date}    ${datetime.now().date()}

Date Conversion Should Fail
    [Arguments]    ${input}    ${error}    ${input_format}=${NONE}
    Run Keyword And Expect Error    ValueError: ${error}
    ...    Convert Date    ${input}    date_format=${input_format}
