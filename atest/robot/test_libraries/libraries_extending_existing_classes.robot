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
    Syslog Should Contain  Imported library 'ExtendPythonLib' with arguments [ ] (version <unknown>, class type, TEST scope, 32 keywords)

Keyword From Java Class Extended By Python Class
    [Tags]  require-jython
    Check Test Case  Keyword From Java Class Extended By Python Class

Keyword From Python Class Extending Java Class
    [Tags]  require-jython
    Check Test Case  Keyword From Python Class Extending Java Class

Method In Python Class Overriding Method In Java Class
    [Tags]  require-jython
    Check Test Case  Method In Python Class Overriding Method in Java Class

Keyword In Python Class Using Method From Java Class
    [Tags]  require-jython
    Check Test Case  Keyword In Python Class Using Method From Java Class

Message Of Importing Library Extending Java Class Should Be In Syslog
    [Tags]  require-jython
    Syslog Should Contain  Imported library 'extendingjava.ExtendJavaLib' with arguments [ ] (version <unknown>, class type, GLOBAL scope, 25 keywords)

Using Methods From Java Parents Should Not Create Handlers Starting With Super__
    [Documentation]  At least in Jython 2.2, when a class implemented in python inherits a java class, and the python class uses a method from the java class, the python instance ends up having an attribute super__methodname, where methodname is the method from parent class. We don't want to create keywords from these, even though they are real methods.
    [Tags]  require-jython
    Syslog Should Not Contain  Created handler 'Super JavaSleep'

