*** Settings ***
Suite Setup     Run Tests  ${EMPTY}
...      test_libraries/as_listener/module_v1_listenerlibrary.robot
Resource        atest_resource.robot

*** Test Cases ***
Module listener with v1 version listener api
    Check Syslog contains    Taking listener 'Listener' into use for library 'module_v1_listenerlibrary' failed:
    ...    Listener 'Listener' does not specify API version.
    ...    Attribute 'ROBOT_LISTENER_API_VERSION' is required.\nListeners are disabled for this library.
    Check Syslog Does Not Contain    Taking listener 'Listener2' into use for library 'module_v1_listenerlibrary' failed:
