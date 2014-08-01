*** Setting ***
Documentation     Tests Robots core importing and importing external modules with same name as Robot's internal modules eg. logging
Suite Setup       Run Module Import Tests
Suite Teardown    Remove Robot Dir
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Variable ***
${DIRNAME}        robot_test_12345
${DIRPATH}        ${CURDIR}${/}${DIRNAME}

*** Test Case ***
Import Logging
    Check testcase    Import Logging

Test Importing Robot Module Directly Fails
    Check testcase    Test Importing Robot Module Directly Fails

Importing Robot Module Through Robot Succeeds
    Check testcase    Importing Robot Module Through Robot Succeeds

*** Keyword ***
Run Module Import Tests
    [Documentation]    Creates robot dir which have caused problems with jython Runs also import tests
    Create Dir    ${DIRPATH}${/}robot
    Run Tests    --pythonpath ${DIRNAME}    core${/}robot_module_importing.html

Remove Robot Dir
    [Documentation]    Removes created robot dir
    Remove Dir    ${DIRPATH}${/}robot
    Remove Dir    ${DIRPATH}
