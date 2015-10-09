*** Settings ***
Resource          libdoc_resource.robot
Test Template     Run Libdoc And Verify Version


*** Test Cases ***

Version defined with ROBOT_LIBRARY_VERSION in Python library
    DynamicLibrary.py::arg    0.1

Version defined with __version__ in Python library
    module.py    0.1-alpha

No version defined in Python library
    NewStyleNoInit.py    ${EMPTY}

Version defined with ROBOT_LIBRARY_VERSION in Java library
    [Tags]    require-jython    require-tools.jar
    Example.java    1.0 <alpha>

No version defined in Java library
    [Tags]    require-jython    require-tools.jar
    NoConstructor.java    ${EMPTY}


*** Keywords ***

Run Libdoc And Verify Version
    [Arguments]    ${library}    ${version}
    Run Libdoc And Parse Output    ${TESTDATADIR}/${library}
    Version Should Be    ${version}
