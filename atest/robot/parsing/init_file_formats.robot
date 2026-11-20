*** Settings ***
Resource        atest_resource.robot

*** Test Cases ***
Init file with '.robot.md' extension
    Run Tests    ${EMPTY}    parsing/init_file_formats/robot_md
    Should Be Equal    ${SUITE.name}    Robot Md
    Should Be Equal    ${SUITE.doc}     Init doc in .robot.md
    Check Log Message    ${SUITE.setup.messages[0]}    Init setup in .robot.md
    Should Contain Tests    ${SUITE}    Example Test

Init file with '.robot.rst' extension
    Run Tests    ${EMPTY}    parsing/init_file_formats/robot_rst
    Should Be Equal    ${SUITE.name}    Robot Rst
    Should Be Equal    ${SUITE.doc}     Init doc in .robot.rst
    Check Log Message    ${SUITE.setup.messages[0]}    Init setup in .robot.rst
    Should Contain Tests    ${SUITE}    Example Test
