*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/nested_try_except.robot

*** Test cases ***
Try except inside try
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    PASS
    Block statuses should be   ${tc.body[0].try_block.body[0]}    FAIL    NOT RUN    NOT RUN    PASS

Try except inside except
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    PASS    NOT RUN
    Block statuses should be   ${tc.body[0].except_blocks[0].body[0]}    FAIL    PASS    PASS

Try except inside try else
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    PASS   NOT RUN    PASS
    Block statuses should be   ${tc.body[0].else_block.body[0]}    FAIL    PASS    PASS

Try except inside finally
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.body[0]}    FAIL    PASS    PASS
    Block statuses should be   ${tc.body[0].finally_block.body[0]}    FAIL    PASS    PASS

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

Try Except in test setup
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.setup.body[0]}    FAIL    PASS

Try Except in test teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.teardown.body[0]}    FAIL    PASS

Failing Try Except in test setup
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.setup.body[0]}    FAIL    NOT RUN

Failing Try Except in test teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.teardown.body[0]}    FAIL    NOT RUN

Failing Try Except in test teardown and other failures
    ${tc}=    Check Test Case    ${TESTNAME}
    Block statuses should be   ${tc.teardown.body[0]}    FAIL    NOT RUN
