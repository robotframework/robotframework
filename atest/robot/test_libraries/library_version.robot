*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/library_version.robot
Resource          atest_resource.robot

*** Test Case ***
Python Library Version
    Check Syslog Contains    Imported library 'classes.VersionLibrary' with arguments [ ] (version 0.1, class type,

Version Undefined In Python Library
    Check Syslog Contains    Imported library 'classes.NameLibrary' with arguments [ ] (version <unknown>, class type,

Module Library Version
    Check Syslog Contains    Imported library 'module_library' with arguments [ ] (version test, module type,

Java Library Version
    [Tags]    require-jython
    Check Syslog Contains    Imported library 'JavaVersionLibrary' with arguments [ ] (version 1.0, class type,

Version Undefined In Java Library
    [Tags]    require-jython
    Check Syslog Contains    Imported library 'ExampleJavaLibrary' with arguments [ ] (version <unknown>, class type,
