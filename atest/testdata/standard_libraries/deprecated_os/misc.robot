*** Settings ***
Suite Teardown    Remove Temps
Test Setup        Remove Temps
Library           OperatingSystem

*** Variables ***
${TESTFILE}       ${CURDIR}${/}robot_temp_file.txt
${TESTDIR}        ${CURDIR}${/}robot_temp_dir

*** Test Cases ***
List Dir
    Create Dir    ${TESTDIR}
    Create File    ${TESTDIR}${/}foo.txt
    Create File    ${TESTDIR}${/}bar.txt
    ${files} =    List Dir    ${TESTDIR}
    Fail Unless    ${files} == ['bar.txt','foo.txt']
    @{files2} =    List Dir    ${TESTDIR}
    Fail Unless Equal    @{files2}[0]    bar.txt
    Fail Unless Equal    @{files2}[1]    foo.txt
    ${file}    @{files3} =    List Dir    ${TESTDIR}
    Fail Unless Equal    ${file}    bar.txt
    Fail Unless Equal    @{files3}[0]    foo.txt
    Remove File    ${TESTDIR}${/}bar.txt
    ${files4} =    List Dir    ${TESTDIR}
    Fail Unless    ${files4} == ['foo.txt']
    @{files5} =    List Dir    ${TESTDIR}
    Fail Unless Equal    @{files5}[0]    foo.txt
    ${file2}    @{files6} =    List Dir    ${TESTDIR}
    Fail Unless Equal    ${file2}    foo.txt
    Fail Unless    @{files6} == []
    Remove File    ${TESTDIR}${/}foo.txt
    ${files7} =    List Dir    ${TESTDIR}
    Fail Unless    ${files7} == []
    @{files8} =    List Dir    ${TESTDIR}
    Fail Unless    @{files8} == []

List Dir With Patterns
    Create Dir    ${TESTDIR}
    Create File    ${TESTDIR}${/}foo.txt
    Create File    ${TESTDIR}${/}bar.txt
    Create Dir    ${TESTDIR}${/}foodir
    ${names} =    List Dir    ${TESTDIR}    *.txt
    Fail Unless    ${names} == ['bar.txt', 'foo.txt']

List Dir With Absolute
    [Documentation]    This tests also List Files In Dir And List Dirs In Dir
    Create Dir    ${TESTDIR}
    Create File    ${TESTDIR}${/}foo.txt
    Create File    ${TESTDIR}${/}bar.txt
    Create Dir    ${TESTDIR}${/}foodir
    ${names} =    List Dir    ${TESTDIR}    ${EMPTY}    yes
    Equals    ${names[0]}    ${TESTDIR}${/}bar.txt
    Equals    ${names[1]}    ${TESTDIR}${/}foo.txt
    Equals    ${names[2]}    ${TESTDIR}${/}foodir
    ${names} =    List Files In Dir    ${TESTDIR}    ${EMPTY}    absolute
    Equals    ${names[0]}    ${TESTDIR}${/}bar.txt
    Equals    ${names[1]}    ${TESTDIR}${/}foo.txt
    ${names} =    List Dirs In Dir    ${TESTDIR}    ${EMPTY}    absolute
    Equals    ${names[0]}    ${TESTDIR}${/}foodir

List And Count Files And Dirs In Dir
    [Documentation]    Tests 'List Files In Dir', 'List Dirs In Dir', 'Count Files In Dir', 'Count Dirs In Dir' and 'Count Items In Dir'
    Create Dir    ${TESTDIR}
    Create File    ${TESTDIR}${/}foo.txt
    Create File    ${TESTDIR}${/}bar.txt
    Create File    ${TESTDIR}${/}zap.txt
    Create Dir    ${TESTDIR}${/}foodir
    Create Dir    ${TESTDIR}${/}bardir
    ${files} =    List Files In Dir    ${TESTDIR}
    ${bar_files} =    List Files In Dir    ${TESTDIR}    bar*
    Fail Unless    ${files} == ['bar.txt','foo.txt','zap.txt']
    Fail Unless    ${bar_files} == ['bar.txt']
    ${dirs} =    List Dirs In Dir    ${TESTDIR}
    ${foo_dirs} =    List Dirs In Dir    ${TESTDIR}    *oo*
    Fail Unless    ${dirs} == ['bardir', 'foodir']
    Fail Unless    ${foo_dirs} == ['foodir']
    ${file_count} =    Count Files In Dir    ${TESTDIR}
    ${txt_file_count} =    Count Files In Dir    ${TESTDIR}    *.txt
    Ints Equal    ${file_count}    3
    Equals    ${file_count}    ${txt_file_count}
    ${dir_count} =    Count Dirs In Dir    ${TESTDIR}
    ${dir_dir_count} =    Count Dirs In Dir    ${TESTDIR}    *dir
    Ints Equal    ${dir_count}    2
    Equals    ${dir_count}    ${dir_dir_count}
    ${count} =    Count Items In Dir    ${TESTDIR}
    ${foo_count} =    Count Items In Dir    ${TESTDIR}    foo*
    Ints Equal    ${count}    5
    Ints Equal    ${foo_count}    2
    ${robot_file_count} =    Count Files In Dir    ${CURDIR}    *.robot
    ${robot_dir_count} =    Count Dirs In Dir    ${CURDIR}    *.robot
    ${robot_item_count} =    Count Items In Dir    ${CURDIR}    *.robot
    Fail Unless    ${robot_file_count} > 0
    Fail Unless Ints Equal    ${robot_dir_count}    0
    Fail Unless Equal    ${robot_file_count}    ${robot_item_count}

*** Keywords ***
Remove Temps
    Remove File    ${TESTFILE}
    Remove Dir    ${TESTDIR}    recursive
