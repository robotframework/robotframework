*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/nested_try_except.robot
Test Template     Verify try except and block statuses

*** Test cases ***
Try except inside try
    FAIL    PASS
    FAIL    NOT RUN    NOT RUN    PASS    path=body[0].body[0].body[0]

Try except inside except
    FAIL    PASS       NOT RUN
    FAIL    PASS       PASS               path=body[0].body[1].body[0]

Try except inside try else
    PASS    NOT RUN    PASS
    FAIL    PASS       PASS               path=body[0].body[2].body[0]

Try except inside finally
    FAIL    PASS       PASS
    FAIL    PASS       PASS               path=body[0].body[-1].body[0]

Try except inside if
    FAIL    PASS                          path=body[0].body[0].body[0]

Try except inside else if
    PASS    NOT RUN    PASS               path=body[0].body[1].body[0]

Try except inside else
    FAIL    PASS                          path=body[0].body[1].body[0]

Try except inside for loop
    PASS    NOT RUN    PASS               path=body[0].body[0].body[0]
    FAIL    PASS       NOT RUN            path=body[0].body[1].body[0]

Try except inside while loop
    PASS    NOT RUN    PASS               path=body[1].body[0].body[0]
    FAIL    PASS       NOT RUN            path=body[1].body[1].body[0]

If inside try failing
    FAIL    PASS       NOT RUN

If inside except handler
    FAIL    PASS       NOT RUN

If inside except handler failing
    FAIL    FAIL       NOT RUN

If inside else block
    PASS    NOT RUN    PASS

If inside else block failing
    PASS    NOT RUN    FAIL

If inside finally block
    FAIL    NOT RUN    PASS               tc_status=FAIL

If inside finally block failing
    PASS    NOT RUN    FAIL

For loop inside try failing
    FAIL    PASS       NOT RUN

For loop inside except handler
    FAIL    PASS       NOT RUN

For loop inside except handler failing
    FAIL    FAIL       NOT RUN

For loop inside else block
    PASS    NOT RUN    PASS

For loop inside else block failing
    PASS    NOT RUN    FAIL

For loop inside finally block
    FAIL    NOT RUN    PASS               tc_status=FAIL

For loop inside finally block failing
    PASS    NOT RUN    FAIL

While loop inside try failing
    FAIL    PASS       NOT RUN

While loop inside except handler
    FAIL    PASS       NOT RUN

While loop inside except handler failing
    FAIL    FAIL       NOT RUN

While loop inside else block
    PASS    NOT RUN    PASS

While loop inside else block failing
    PASS    NOT RUN    FAIL

While loop inside finally block
    FAIL    NOT RUN    PASS               tc_status=FAIL

While loop inside finally block failing
    PASS    NOT RUN    FAIL

Try Except in test setup
    FAIL    PASS                          path=setup.body[0]

Try Except in test teardown
    FAIL    PASS                          path=teardown.body[0]

Failing Try Except in test setup
    FAIL    NOT RUN                       path=setup.body[0]

Failing Try Except in test teardown
    FAIL    NOT RUN                       path=teardown.body[0]

Failing Try Except in test teardown and other failures
    FAIL    NOT RUN                       path=teardown.body[0]
