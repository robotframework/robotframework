*** Settings ***
Suite Setup      Run Tests    --pythonpath "${LIBS}:${LIBS}/dir_for_libs"    test_libraries/package_library.robot
Resource         atest_resource.robot

*** Variables ***
${LIBS}          ${DATADIR}/test_libraries

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
Import message should be syslogged
    [Arguments]    ${name}    ${file}=__init__    ${type}=class
    ${base} =    Normalize Path    ${DATADIR}/test_libraries/MyLibDir
    Syslog Should Contain    | INFO \ |
    ...    Imported library ${type} '${name}' from '${base}${/}${file}
