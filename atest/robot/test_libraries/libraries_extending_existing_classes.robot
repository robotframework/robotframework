*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/libraries_extending_existing_classes.robot
Resource        atest_resource.robot

*** Test Cases ***
Keyword From Python Class Extended By Python Class
    Check Test Case  Keyword From Python Class Extended By Python Class

Keyword From Python Class Extending Python Class
    Check Test Case  Keyword From Python Class Extending Python class

Method In Python Class Overriding Method Of The Parent Class
    Check Test Case  Method In Python Class Overriding Method Of The Parent Class

Keyword In Python Class Using Method From Parent Class
    Check Test Case  Keyword In Python Class Using Method From Parent Class

Message Of Importing Library Should Be In Syslog
    Syslog Should Contain  Imported library 'ExtendPythonLib' with arguments [ ] (version <unknown>, class type, TEST scope, 31 keywords)
