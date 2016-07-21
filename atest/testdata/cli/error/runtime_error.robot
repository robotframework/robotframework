*** Settings ***
Suite Teardown    No Operation
Test Teardown     No Operation

*** Test Cases ***
Before Error
    No Operation

Runtime Error
    [Documentation]    Not sure could errors really even happen at runtime...
    Evaluate    robot.output.LOGGER.error('Runtime error')    modules=robot

After Error
    No Operation
