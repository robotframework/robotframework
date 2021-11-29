*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/nested_try_except.robot

*** Test cases ***
Try except inside if
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0].body[0].body[0]}    FAIL    PASS

Try except inside else if
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0].body[1].body[0]}    PASS    NOT RUN    PASS

Try except inside else
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0].body[1].body[0]}    FAIL    PASS

Try except inside for loop
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0].body[0].body[0]}    PASS    NOT RUN    PASS
    Block statuses should be   ${tc.body[0].body[1].body[0]}    FAIL    PASS    NOT RUN

If inside try failing
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    PASS    NOT RUN

If inside except handler
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    PASS    NOT RUN

If inside except handler failing
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    FAIL    NOT RUN

If inside else block
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    PASS    NOT RUN    PASS

If inside else block failing
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    PASS    NOT RUN    FAIL

If inside finally block
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    NOT RUN    PASS

If inside finally block failing
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    PASS    NOT RUN    FAIL

For loop inside try failing
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    PASS    NOT RUN

For loop inside except handler
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    PASS    NOT RUN

For loop inside except handler failing
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    FAIL    NOT RUN

For loop inside else block
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    PASS    NOT RUN    PASS

For loop inside else block failing
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    PASS    NOT RUN    FAIL

For loop inside finally block
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    NOT RUN    PASS

For loop inside finally block failing
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    PASS    NOT RUN    FAIL
