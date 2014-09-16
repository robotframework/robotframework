*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/deprecated_os/misc.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***
List Dir
    Check testcase  List Dir

List Dir With Patterns
    Check testcase  List Dir With Patterns

List Dir With Absolute
    Check testcase  List Dir With Absolute

List And Count Files And Dirs In Dir
    [Documentation]  Tests 'List Files In Dir', 'List Dirs In Dir', 'Count Files In Dir', 'Count Dirs In Dir' and 'Count Items In Dir'
    Check testcase  List And Count Files And Dirs In Dir

