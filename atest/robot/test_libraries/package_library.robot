*** Settings ***
Suite Setup      Set PYTHONPATH and run tests
Resource         atest_resource.robot

*** Test Cases ***
Class in package as library implicitly
    Check Test Case    ${TESTNAME}
    Import message should be syslogged    MyLibDir

Class in package as library explicitly
    Check Test Case    ${TESTNAME}
    Import message should be syslogged    MyLibDir.MyLibDir

Package itself as library
    Check Test Case    ${TESTNAME}

Class in sub-module as library implicitly
    Check Test Case    ${TESTNAME}

Class in sub-module as library explicitly
    Check Test Case    ${TESTNAME}

Sub-module itself as library
    Check Test Case    ${TESTNAME}
    Import message should be syslogged    MyLibDir.SubModuleLib    SubModuleLib    module

Class in sub-package as library implicitly
    Check Test Case    ${TESTNAME}
    Import message should be syslogged    MyLibDir.SubPackage    SubPackage${/}__init__

Class in sub-package as library explicitly
    Check Test Case    ${TESTNAME}
    Import message should be syslogged    MyLibDir.SubPackage.SubPackage    SubPackage${/}__init__

Sub-package itself as library
    Check Test Case    ${TESTNAME}

Class in sub-sub-module as library implicitly
    Check Test Case    ${TESTNAME}

Class in sub-sub-module as library explicitly
    Check Test Case    ${TESTNAME}

Sub-sub-module itself as library
    Check Test Case    ${TESTNAME}

*** Keywords ***
Set PYTHONPATH and run tests
    ${dir} =    Normalize Path    ${DATADIR}/test_libraries
    Set PYTHONPATH    ${dir}    ${dir}${/}dir_for_libs
    Run Tests    ${EMPTY}    test_libraries/package_library.robot
    [Teardown]    Reset PYTHONPATH

Import message should be syslogged
    [Arguments]    ${name}    ${file}=__init__    ${type}=class
    ${base} =    Normalize Path    ${DATADIR}/test_libraries/MyLibDir
    Syslog Should Contain    | INFO \ |
    ...    Imported test library ${type} '${name}' from '${base}${/}${file}
