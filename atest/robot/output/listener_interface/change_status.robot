*** Settings ***
Suite Setup       Run Tests    --listener ${DATADIR}/${MODIFIER}    ${SOURCE}
Resource          atest_resource.robot

*** Variables ***
${SOURCE}         output/listener_interface/body_items_v3/change_status.robot
${MODIFIER}       output/listener_interface/body_items_v3/ChangeStatus.py

*** Test Cases ***
Fail to pass
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Fail    args=Pass me!        status=PASS       message=Failure hidden!
    Check Log Message     ${tc[0][0]}    Pass me!    level=FAIL
    Check Keyword Data    ${tc[1]}    BuiltIn.Log     args=I'm run.        status=PASS       message=

Pass to fail
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Log     args=Fail me!        status=FAIL       message=Ooops!!
    Check Log Message     ${tc[0][0]}    Fail me!    level=INFO
    Check Keyword Data    ${tc[1]}    BuiltIn.Log     args=I'm not run.    status=NOT RUN    message=

Pass to fail without a message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Log     args=Silent fail!    status=FAIL       message=
    Check Keyword Data    ${tc[1]}    BuiltIn.Log     args=I'm not run.    status=NOT RUN    message=

Skip to fail
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Skip    args=Fail me!        status=FAIL       message=Failing!
    Check Log Message     ${tc[0][0]}    Fail me!    level=SKIP
    Check Keyword Data    ${tc[1]}    BuiltIn.Log     args=I'm not run.    status=NOT RUN    message=

Fail to skip
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Fail    args=Skip me!        status=SKIP       message=Skipping!
    Check Log Message     ${tc[0][0]}    Skip me!    level=FAIL
    Check Keyword Data    ${tc[1]}    BuiltIn.Log     args=I'm not run.    status=NOT RUN    message=

Not run to fail
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Log     args=Fail me!        status=FAIL       message=Ooops!!
    Check Keyword Data    ${tc[1]}    BuiltIn.Log     args=I'm not run.    status=NOT RUN    message=
    Check Keyword Data    ${tc[2]}    BuiltIn.Log     args=Fail me!        status=FAIL       message=Failing without running!
    Check Keyword Data    ${tc[3]}    BuiltIn.Log     args=I'm not run.    status=NOT RUN    message=

Pass and fail to not run
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Log     args=Mark not run!   status=NOT RUN    message=
    Check Keyword Data    ${tc[1]}    BuiltIn.Fail    args=Mark not run!   status=NOT RUN    message=Mark not run!
    Check Keyword Data    ${tc[2]}    BuiltIn.Fail    args=I fail!         status=FAIL       message=I fail!

Only message
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Fail    args=Change me!      status=FAIL       message=Changed!
    Check Keyword Data    ${tc[1]}    Change message                       status=NOT RUN    message=Changed!

Control structures
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Control Structure    ${tc[0]}    FOR
    Check Control Structure    ${tc[1]}    WHILE
    Check Control Structure    ${tc[2]}    IF/ELSE ROOT
    Check Control Structure    ${tc[3]}    TRY/EXCEPT ROOT

*** Keywords ***
Check Control Structure
    [Arguments]    ${item}    ${type}
    VAR                   ${msg}                     Handled on ${type} level.
    Should Be Equal       ${item.type}               ${type}
    Should Be Equal       ${item.status}             PASS
    Should Be Equal       ${item.message}            ${msg}
    Should Be Equal       ${item[0].status}     FAIL
    Should Be Equal       ${item[0].message}    ${msg}
    Check Keyword Data    ${item[0, 0]}    BuiltIn.Fail    args=${msg}    status=FAIL    message=${msg}
