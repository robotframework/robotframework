*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/library_decorator.robot
Resource          atest_resource.robot

*** Test Cases ***
Set Library Version And Scope Using Library Decorator
    Check Syslog Contains    LibraryDecorator.py' with arguments [ ] (version 1.2.3, class type, test suite scope, 1 keywords)

Library Decorator Disables Public Methods
    Check Test Case  ${TESTNAME}

Library Decorator Does Not Disable Decorated Public Methods
    Check Test Case  ${TESTNAME}
