*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/screenshot/set_screenshot_directory.robot
Force Tags      require-screenshot
Resource        atest_resource.robot

*** Test Cases ***
Set Screenshot Directory
    Check Test Case  ${TESTNAME}
