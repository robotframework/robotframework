*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/new_style_classes.robot
Resource          atest_resource.robot

*** Test Case ***
Keyword From New Style Class Library
    Check Test Case    Keyword From New Style Class Library
    Check Syslog Contains    Imported library 'newstyleclasses.NewStyleClassLibrary' with arguments [ ] (version <unknown>, class type, testcase scope, 1 keywords

Keyword From Library With Metaclass
    Check Test Case    Keyword From Library With Metaclass
    Check Syslog Contains    Imported library 'newstyleclasses.MetaClassLibrary' with arguments [ ] (version <unknown>, class type, testcase scope, 2 keywords

Keyword Created By Metaclass
    Check Test Case    Keyword Created By Metaclass

Methods in Metaclass Are not Keywords
    Check Test Case    Methods in Metaclass Are not Keywords
