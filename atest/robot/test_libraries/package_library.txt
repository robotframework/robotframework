*** Settings ***
Suite Setup      Set PYTHONPATH and run tests
Force Tags       regression    pybot    jybot
Resource         atest_resource.txt

*** Test Cases ***
Class in package as library implicitly
    Check Test Case    ${TESTNAME}

Class in package as library explicitly
    Check Test Case    ${TESTNAME}

Package itself as library
    Check Test Case    ${TESTNAME}

Class in sub-module as library implicitly
    Check Test Case    ${TESTNAME}

Class in sub-module as library explicitly
    Check Test Case    ${TESTNAME}

Sub-module itself as library
    Check Test Case    ${TESTNAME}

Class in sub-package as library implicitly
    Check Test Case    ${TESTNAME}

Class in sub-package as library explicitly
    Check Test Case    ${TESTNAME}

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
    Append To Environment Variable    PYTHONPATH    ${dir}    ${dir}${/}dir_for_libs
    Run Tests    ${EMPTY}    test_libraries/package_library.txt
