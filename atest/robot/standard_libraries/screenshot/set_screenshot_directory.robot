*** Settings ***
Suite Setup     Run if dependencies are available  ${EMPTY}  standard_libraries/screenshot/set_screenshot_directory.robot
Force Tags      regression
Resource        screenshot_resource.robot

*** Test Cases ***
Set Screenshot Directory
    ${tc}=  Check Test Case  ${TESTNAME}
