*** Settings ***
Documentation   Tests for BuiltIn library's keyword Get Time
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/get_time.robot
Resource        atest_resource.robot

*** Test Cases ***
Get Time As Timestamp
    Check Test Case  ${TEST NAME}

Get Time As Seconds After Epoch
    Check Test Case  ${TEST NAME}

Get Time As Parts
    Check Test Case  ${TEST NAME}

When Time Is Seconds After Epoch
    Check Test Case  ${TEST NAME}

When Time Is Timestamp
    Check Test Case  ${TEST NAME}

When Time Is Now
    Check Test Case  ${TEST NAME}

When Time Is Now +- something
    Check Test Case  ${TEST NAME}

Empty Format Is Interpreted As Timestamp When Time Given
    Check Test Case  ${TEST NAME}

Invalid Time Does Not Cause Un-Catchable Failure
    Check Test Case  ${TEST NAME}

When Time Is UTC
    Check Test Case  ${TEST NAME}

When Time Is UTC +- something
    Check Test Case  ${TEST NAME}

DST is handled correctly when adding or substracting time
    Check Test Case  ${TEST NAME}
