*** Settings ***
Resource          resource_with_error.robot
Suite Teardown    No Operation
Test Teardown     No Operation

*** Test Cases ***
Resource Error
    No Operation
