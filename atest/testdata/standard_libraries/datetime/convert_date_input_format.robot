*** Settings ***
Test Template     Date Conversion Should Succeed
Library           DateTime
Variables         datesandtimes.py

*** Test Cases ***    INPUT                                           OUTPUT                     INPUT FORMAT
String inputs         2014-04-24 21:45:12.123                         2014-04-24 21:45:12.123
                      2014-04-24 21:45:12                             2014-04-24 21:45:12.000
                      2014-04-24T21:45:12.123                         2014-04-24 21:45:12.123
                      2014.04+24@@21/45!12,123                        2014-04-24 21:45:12.123
                      2014foo06bar05                                  2014-06-05 00:00:00.000

Formatted strings     2014-04-24 21:45:12.123                         2014-04-24 21:45:12.123    %Y-%m-%d %H:%M:%S.%f
                      2014-04-24T21:45:12.123                         2014-04-24 21:45:12.123    %Y-%m-%dT%H:%M:%S.%f
                      24.4.2014 21:45:12-123                          2014-04-24 21:45:12.123    %d.%m.%Y %H:%M:%S-%f
                      04/24/2014T21.45.12                             2014-04-24 21:45:12.000    %m/%d/%YT%H.%M.%S
                      24.04.2014                                      2014-04-24 00:00:00.000    %d.%m.%Y
                      24-04.2014@21                                   2014-04-24 21:00:00.000    %d-%m.%Y@%H

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
                      2014-04-24T21:45:12.123456                      2014-04-24 21:45:12.123    %Y-%m-%dT%H:%M:%S.%f
                      2014-04-24T21:45:12.1234                        2014-04-24 21:45:12.123    %Y-%m-%dT%H:%M:%S.%f
                      2014-04-24T21:45:12.1235                        2014-04-24 21:45:12.124    %Y-%m-%dT%H:%M:%S.%f
                      ${EPOCH + 0.123456}                             2018-11-22 13:13:42.123
                      ${EPOCH + 0.1234}                               2018-11-22 13:13:42.123
                      ${EPOCH + 0.5}                                  2018-11-22 13:13:43        exclude_millis=True
                      ${EPOCH - 0.5}                                  2018-11-22 13:13:42        exclude_millis=True
                      ${datetime(2014, 4, 24, 21, 45, 12, 123456)}    2014-04-24 21:45:12.123
                      ${datetime(2014, 4, 24, 21, 45, 12, 123400)}    2014-04-24 21:45:12.123
                      ${datetime(2014, 4, 24, 21, 45, 12, 123500)}    2014-04-24 21:45:12.124

Formatted with %f in middle
    [Template]     NONE
    Run Keyword If    sys.platform == 'cli'
    ...   Run Keyword And Expect Error    ValueError: %f directive is supported only at the end of the format string on this Python interpreter.
    ...   Date Conversion Should Succeed    21:45:12.123 24.04.2014    2014-04-24 21:45:12.123    %H:%M:%S.%f %d.%m.%Y
    ...   ELSE
    ...   Date Conversion Should Succeed    21:45:12.123 24.04.2014    2014-04-24 21:45:12.123    %H:%M:%S.%f %d.%m.%Y

Invalid input
    [Template]    Date Conversion Should Fail
    kekkonen      Invalid timestamp 'kekkonen'.
    2014-06       Invalid timestamp '2014-06'.
    2014-06-5     Invalid timestamp '2014-06-5'.
    2014-06-05    *                                 %Y-%m-%d %H:%M:%S.%f
    2015-xxx      *                                 %Y-%f
    ${NONE}       Unsupported input 'None'.

*** Keywords ***
Date Conversion Should Succeed
    [Arguments]    ${input}    ${expected}    ${input_format}=${NONE}    &{config}
    ${ts} =    Convert Date    ${input}    date_format=${input_format}    &{config}
    Should Be Equal    ${ts}    ${expected}

Date Conversion Should Fail
    [Arguments]    ${input}    ${error}    ${input_format}=${NONE}
    Run Keyword And Expect Error    ValueError: ${error}
    ...    Convert Date    ${input}    date_format=${input_format}
