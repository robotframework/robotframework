*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/new_style_classes.robot
Resource          atest_resource.robot

*** Test Cases ***
Keyword From New Style Class Library
    Check Test Case    Keyword From New Style Class Library
    Syslog Should Contain    Imported library 'newstyleclasses.NewStyleClassLibrary' with arguments [ ] (version <unknown>, class type, TEST scope, 1 keywords

Keyword From Library With Metaclass
    Check Test Case    Keyword From Library With Metaclass
    Syslog Should Contain    Imported library 'newstyleclasses.MetaClassLibrary' with arguments [ ] (version <unknown>, class type, TEST scope, 2 keywords

Keyword Created By Metaclass
    Check Test Case    Keyword Created By Metaclass

Methods in Metaclass Are not Keywords
    Check Test Case    Methods in Metaclass Are not Keywords
