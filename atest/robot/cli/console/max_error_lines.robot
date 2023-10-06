*** Settings ***
Documentation     Testing that long error messages over a set limit are truncated
Resource          atest_resource.robot

*** Variables ***
${EXPLANATION}    \n${SPACE*4}\[ Message content over the limit has been removed. \]\n
${3DOTS}          \\.\\.\\.

*** Test Cases ***
Max Error Lines 30
    Run Tests    --maxerrorlines 30    cli/console/max_error_lines.robot
    Has Not Been Cut    150 X 14 Message Under The Limit
    Has Not Been Cut    2340 x 1 Message On The Limit
    Has Been Cut    8 x 31 Message Over The Limit
    Has Been Cut    400 x 7 Message Over The Limit    801.*${3DOTS}    ${3DOTS}.*END

Max Error Lines 100
    Run Tests    --maxerrorlines 100    cli/console/max_error_lines.robot
    Has Not Been Cut    150 X 49 Message Under The Limit
    Has Not Been Cut    7800 x 1 Message On The Limit
    Has Been Cut    8 x 101 Message Over The Limit
    Has Been Cut    1500 x 7 Message Over The Limit    3001.*${3DOTS}    ${3DOTS}.*END

Max Error Lines None
    Run Tests    --maxerrorlines NONE    cli/console/max_error_lines.robot
    Has Not Been Cut    8 x 101 Message Over The Limit

Invalid Values
    Run Tests Without Processing Output    --maxerrorlines InVaLid    misc/pass_and_fail.robot
    Stderr Should Be Equal To    [ ERROR ] Invalid value for option '--maxerrorlines': Expected integer, got 'InVaLid'.${USAGE TIP}\n
    Run Tests Without Processing Output    --maxerrorlines -100    misc/pass_and_fail.robot
    Stderr Should Be Equal To    [ ERROR ] Invalid value for option '--maxerrorlines': Expected integer greater than 10, got -100.${USAGE TIP}\n

*** Keywords ***
Has Been Cut
    [Arguments]    ${test}    ${eol_dots}=    ${bol_dots}=
    ${test} =    Get Test Case    ${test}
    Should Contain    ${test.message}    ${EXPLANATION}
    Should Match Non Empty Regexp    ${test.message}    ${eol_dots}
    Should Match Non Empty Regexp    ${test.message}    ${bol_dots}
    Error Message In Log Should Not Have Been Cut    ${test.kws}
    RETURN    ${test}

Error Message In Log Should Not Have Been Cut
    [Arguments]    ${kws}
    @{keywords} =    Set Variable    ${kws}
    FOR    ${kw}    IN    @{keywords}
        Run Keyword If    ${kw.msgs}    Should Not Contain    ${kw.msgs[-1].message}    ${EXPLANATION}
        Error Message In Log Should Not Have Been Cut    ${kw.kws}
    END

Should Match Non Empty Regexp
    [Arguments]    ${message}    ${pattern}
    IF    $pattern    Should Match Regexp    ${message}    ${pattern}

Has Not Been Cut
    [Arguments]    ${testname}
    ${test} =    Get Test Case    ${testname}
    Should Not Contain    ${test.message}    Message content over
