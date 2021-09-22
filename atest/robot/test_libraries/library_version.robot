*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/library_version.robot
Resource          atest_resource.robot

*** Test Case ***
Python Library Version
    Syslog Should Contain    Imported library 'classes.VersionLibrary' with arguments [ ] (version 0.1, class type,

Version Undefined In Python Library
    Syslog Should Contain    Imported library 'classes.NameLibrary' with arguments [ ] (version <unknown>, class type,

Module Library Version
    Syslog Should Contain    Imported library 'module_library' with arguments [ ] (version test, module type,
