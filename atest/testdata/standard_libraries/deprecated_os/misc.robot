*** Settings ***
Suite Teardown    Remove Temps
Test Setup        Remove Temps
Library           OperatingSystem

*** Variables ***
${TESTFILE}       ${CURDIR}${/}robot_temp_file.txt
${TESTDIR}        ${CURDIR}${/}robot_temp_dir

*** Test Cases ***
List Dir
    Create Directory    ${TESTDIR}
    Create File    ${TESTDIR}${/}foo.txt
    Create File    ${TESTDIR}${/}bar.txt
    ${files} =    List Dir    ${TESTDIR}
    Should Be True    ${files} == ['bar.txt','foo.txt']
    @{files2} =    List Dir    ${TESTDIR}
    Should Be Equal    @{files2}[0]    bar.txt
    Should Be Equal    @{files2}[1]    foo.txt
    ${file}    @{files3} =    List Dir    ${TESTDIR}
    Should Be Equal    ${file}    bar.txt
    Should Be Equal    @{files3}[0]    foo.txt
    Remove File    ${TESTDIR}${/}bar.txt
    ${files4} =    List Dir    ${TESTDIR}
    Should Be True    ${files4} == ['foo.txt']
    @{files5} =    List Dir    ${TESTDIR}
    Should Be Equal    @{files5}[0]    foo.txt
    ${file2}    @{files6} =    List Dir    ${TESTDIR}
    Should Be Equal    ${file2}    foo.txt
    Should Be True    @{files6} == []
    Remove File    ${TESTDIR}${/}foo.txt
    ${files7} =    List Dir    ${TESTDIR}
    Should Be True    ${files7} == []
    @{files8} =    List Dir    ${TESTDIR}
    Should Be True    @{files8} == []

List Dir With Patterns
    Create Directory    ${TESTDIR}
    Create File    ${TESTDIR}${/}foo.txt
    Create File    ${TESTDIR}${/}bar.txt
    Create Directory    ${TESTDIR}${/}foodir
    ${names} =    List Dir    ${TESTDIR}    *.txt
    Should Be True    ${names} == ['bar.txt', 'foo.txt']

List Dir With Absolute
    [Documentation]    This tests also List Files In Dir And List Dirs In Dir
    Create Directory    ${TESTDIR}
    Create File    ${TESTDIR}${/}foo.txt
    Create File    ${TESTDIR}${/}bar.txt
    Create Directory    ${TESTDIR}${/}foodir
    ${names} =    List Dir    ${TESTDIR}    ${EMPTY}    yes
    Should Be Equal    ${names[0]}    ${TESTDIR}${/}bar.txt
    Should Be Equal    ${names[1]}    ${TESTDIR}${/}foo.txt
    Should Be Equal    ${names[2]}    ${TESTDIR}${/}foodir
    ${names} =    List Files In Dir    ${TESTDIR}    ${EMPTY}    absolute
    Should Be Equal    ${names[0]}    ${TESTDIR}${/}bar.txt
    Should Be Equal    ${names[1]}    ${TESTDIR}${/}foo.txt
    ${names} =    List Dirs In Dir    ${TESTDIR}    ${EMPTY}    absolute
    Should Be Equal    ${names[0]}    ${TESTDIR}${/}foodir

List And Count Files And Dirs In Dir
    [Documentation]    Tests 'List Files In Dir', 'List Dirs In Dir', 'Count Files In Dir', 'Count Dirs In Dir' and 'Count Items In Dir'
    Create Directory    ${TESTDIR}
    Create File    ${TESTDIR}${/}foo.txt
    Create File    ${TESTDIR}${/}bar.txt
    Create File    ${TESTDIR}${/}zap.txt
    Create Directory    ${TESTDIR}${/}foodir
    Create Directory    ${TESTDIR}${/}bardir
    ${files} =    List Files In Dir    ${TESTDIR}
    ${bar_files} =    List Files In Dir    ${TESTDIR}    bar*
    Should Be True    ${files} == ['bar.txt','foo.txt','zap.txt']
    Should Be True    ${bar_files} == ['bar.txt']
    ${dirs} =    List Dirs In Dir    ${TESTDIR}
    ${foo_dirs} =    List Dirs In Dir    ${TESTDIR}    *oo*
    Should Be True    ${dirs} == ['bardir', 'foodir']
    Should Be True    ${foo_dirs} == ['foodir']
    ${file_count} =    Count Files In Dir    ${TESTDIR}
    ${txt_file_count} =    Count Files In Dir    ${TESTDIR}    *.txt
    Should Be Equal As Integers    ${file_count}    3
    Should Be Equal    ${file_count}    ${txt_file_count}
    ${dir_count} =    Count Dirs In Dir    ${TESTDIR}
    ${dir_dir_count} =    Count Dirs In Dir    ${TESTDIR}    *dir
    Should Be Equal As Integers    ${dir_count}    2
    Should Be Equal    ${dir_count}    ${dir_dir_count}
    ${count} =    Count Items In Dir    ${TESTDIR}
    ${foo_count} =    Count Items In Dir    ${TESTDIR}    foo*
    Should Be Equal As Integers    ${count}    5
    Should Be Equal As Integers    ${foo_count}    2
    ${robot_file_count} =    Count Files In Dir    ${CURDIR}    *.robot
    ${robot_dir_count} =    Count Dirs In Dir    ${CURDIR}    *.robot
    ${robot_item_count} =    Count Items In Dir    ${CURDIR}    *.robot
    Should Be True    ${robot_file_count} > 0
    Should Be Equal As Integers    ${robot_dir_count}    0
    Should Be Equal    ${robot_file_count}    ${robot_item_count}

*** Keywords ***
Remove Temps
    Remove File    ${TESTFILE}
    Remove Directory    ${TESTDIR}    recursive
