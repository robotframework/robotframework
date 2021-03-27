*** Settings ***
Documentation   Testing logging behaviour from non-main threads.
Resource        atest_resource.robot


*** Variables ***
${TIMESTAMP}   ???????? ??:??:??.???
${MAINLINE SUITE TEST}  Log messages from non-main threads should be ignored
${SUITE FILE}  test_libraries/non_main_threads_logging.robot


*** Test Cases ***
Log messages from non-main threads should be ignored
    [Documentation]  Run the mainline test without debugfile enabled. Check
    ...              that all logs from non-main threads are ignored.
    Run Tests    -t "${MAINLINE SUITE TEST}"    ${SUITE FILE}
    ${tc} =  Check Test Case  ${MAINLINE SUITE TEST}
    Check Log Messages In Main Testcase  ${tc}

Log messages from non-main threads should be written to debug file
    [Documentation]  Run the mainline test with debugfile enabled. Check that
    ...              all logs from non-main threads are ignored in all output
    ...              except the debugfile, which should contain all the
    ...              messages logged by all threads, without log lines having
    ...              been written over each other.
    Run Tests    --debugfile debug.log -t "${MAINLINE SUITE TEST}"    ${SUITE FILE}
    ${tc} =  Check Test Case  ${MAINLINE SUITE TEST}
    Check Log Messages In Main Testcase  ${tc}
    ${content} =  Get File  ${OUTDIR}/debug.log
    Check Main Thread Debugfile Logs  ${content}
    Check Thread Debugfile Logs      ${content}


*** Keywords ***
Check Log Messages In Main Testcase
    [Documentation]  Check that the messages logged in the main testcase for
    ...              this suite (Log messages from non-main threads should be
    ...              ignored) are as expected.
    [Arguments]    ${tc}
    Should Be Empty      ${tc.kws[0].msgs}
    Should Be Empty      ${tc.kws[1].msgs}
    Check Log Message    ${tc.kws[2].msgs[0]}      0
    Check Log Message    ${tc.kws[2].msgs[99]}    99
    Length Should Be     ${tc.kws[3].msgs}       100
    Check Log Message    ${tc.kws[3].msgs[0]}      0
    Check Log Message    ${tc.kws[3].msgs[99]}    99
    Length Should Be     ${tc.kws[3].msgs}       100

Debugfile Should Contain
    [Documentation]  Check that the debugfile contents provided contain the
    ...              specified lines the specified number of times (default 1).
    [Arguments]  ${content}  @{lines}  ${count}=None
    Should Not Be Empty  ${lines}  Invalid usage!!
    ${expected} =  Catenate  SEPARATOR=\n  @{lines}
    IF    not ${count}
        Should Match  ${content}  *${expected}*
    ELSE
        ${full_expected} =  Set Variable  ${expected}
        FOR  ${counter}  IN RANGE  ${count}
            ${full_expected} =  Catenate  SEPARATOR=*  ${full_expected}  ${expected}
        END
        Should Match  ${content}  *${full_expected}*
    END

Get Thread Logged String
    [Documentation]  Get the string logged in a thread as part of the main
    ...              testcase.
    [Arguments]  ${thread_id}  ${base_log}  ${count}  ${level}
    ${log_string} =  Set Variable  ${TIMESTAMP} - ${level} - ${thread_id} - ${base_log}
    FOR  ${counter}  IN RANGE  1  ${count}
        ${log_string} =  Catenate  SEPARATOR=  ${log_string}  ${base_log}
    END
    ${log_string} =  Catenate  SEPARATOR=  ${TIMESTAMP}
    [Return]  ${log_string}

Check Thread Debugfile Logs
    [Documentation]  Check that the messages logged by threads in the testcase
    ...              to debugfile match the expected values.
    ...
    ...              For each of the two threads, we should get all of the
    ...              logged messages at the correct log level.
    [Arguments]  ${content}
    FOR  ${thread}  IN  Thread-1  Thread-2
        FOR  ${counter}  IN RANGE  100
            Log  Checking expected line for thread ${thread} count ${counter}

            ${thread_logged_string} =  Get Thread Logged String
            ...    ${thread}  In thread ${thread}: ${counter}\n  20  WARN
            Debugfile Should Contain  ${content}  ${thread_logged_string}

            ${thread_logged_string} =  Get Thread Logged String
            ...  ${thread}  Debugging in thread ${thread}: ${counter}\n  10  DEBUG
            Debugfile Should Contain  ${content}  ${thread_logged_string}
        END
    END

Check Main Thread Debugfile Logs
    [Documentation]  Check that the messages logged by the main thread in the
    ...              testcase to debugfile match the expected values.
    ...
    ...              We should get each of the non-threaded messages. Since we
    ...              get one of each of the numbers logged at INFO level for
    ...              the two keywords, one using Robot logger and the other
    ...              Python logging module, we check for at least two matches
    ...              of each of the log lines.
    [Arguments]  ${content}
    FOR  ${counter}  IN RANGE  100
        ${log_string} =  Set Variable  ${TIMESTAMP} - INFO - MainThread - ${counter}\n
        Debugfile Should Contain  ${content}  ${log_string}*${log_string}
    END

