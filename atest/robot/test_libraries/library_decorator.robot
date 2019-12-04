*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/library_decorator.robot
Resource          atest_resource.robot

*** Test Cases ***
Set Library Version And Scope Using Library Decorator
    Check Syslog Contains    LibraryDecoratorWithArgs.py' with arguments [ ] (version 1.2.3, class type, test suite scope, 1 keywords)

Library Decorator With Args Disables Public Methods
    Check Test Case  ${TESTNAME}

Library Decorator With Args Does Not Disable Decorated Public Methods
    Check Test Case  ${TESTNAME}

Public Method From Library Decorator Is Not Recognized As Keyword
    Check Test Case  ${TESTNAME}

Decorated Method From Libary Decorator Is Recognized As Keyword
    Check Test Case  ${TESTNAME}
