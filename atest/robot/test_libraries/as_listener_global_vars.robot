*** Settings ***
Test Setup       Run Tests    ${EMPTY}    test_libraries/as_listener/global_vars_listener.robot
Resource         atest_resource.robot

*** Test Cases ***
Check global variables in 'close' listener method
    Stderr Should Be Equal To    SEPARATOR=\n
        ...  Suite name:Global Vars Listener
        ...  Suite documentation:Test global variables in 'close' listener method
        ...  Previous test name:
        ...  Previous test status:
        ...  Log level:INFO
        ...  Suite name:Global Vars Listener
        ...  Suite documentation:Test global variables in 'close' listener method
        ...  Previous test name:Global variables test
        ...  Previous test status:PASS
        ...  Log level:INFO
        ...  Suite name:Global Vars Listener
        ...  Suite documentation:Test global variables in 'close' listener method
        ...  Previous test name:Global variables final test
        ...  Previous test status:PASS
        ...  Log level:INFO\n
