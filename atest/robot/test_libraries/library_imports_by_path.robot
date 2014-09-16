*** Settings ***
Documentation   Importing test libraries using relative and absolute path.
Suite Setup     Run Tests  ${EMPTY}  test_libraries/library_import_by_path.robot
Force Tags      regression
Default Tags    pybot  jybot
Resource        atest_resource.robot

*** Test Cases ***
Importing Python Library In File By Path
    ${test} =  Check Test Case  Importing Python Library In File By Path
    Should Be Equal  ${test.kws[0].name}  MyLibFile.Keyword In My Lib File
    Should Be Equal  ${test.kws[1].name}  \${ret} = MyLibFile2.Keyword In My Lib File 2

Importing Python Library In Dir By Path
    ${test} =  Check Test Case  Importing Python Library In Dir By Path
    Should Be Equal  ${test.kws[0].name}  \${ret} = MyLibDir.Keyword In My Lib Dir
    Should Be Equal  ${test.kws[2].name}  \${ret} = MyLibDir.Keyword In My Lib Dir

Importing Library With Same Name
    ${tc} =  Check Test Case  ${TEST NAME}
    Check log message  ${tc.kws[0].msgs[0]}  Hello from lib1
    Check log message  ${tc.kws[1].msgs[0]}  Hello from lib2

Importing Python Library By Path With Variables
    ${test} =  Check Test Case  Importing Python Library By Path With Variables
    Should Be Equal  ${test.kws[0].name}  \${sum} = MyLibDir2.Keyword In My Lib Dir 2

Importing Java Library File By Path With .java Extension
    [Tags]  jybot
    ${test} =  Check Test Case  Importing Java Library File By Path With .java Extension
    Should Be Equal  ${test.kws[0].name}  \${ret} = MyJavaLib.Keyword In My Java Lib

Importing Java Library File By Path With .class Extension
    [Tags]  jybot
    ${test} =  Check Test Case  Importing Java Library File By Path With .class Extension
    Should Be Equal  ${test.kws[0].name}  \${ret} = MyJavaLib2.Keyword In My Java Lib 2

Importing By Path Having Spaces
    Check Test Case  Importing By Path Having Spaces

Importing Invalid Python File Fails
    ${path} =  Normalize Path  ${DATADIR}/test_libraries/MyInvalidLibFile.py
    Check Stderr Contains  Importing test library '${path}' failed:  ImportError: I'm not really a library!

Importing Dir Library Without Trailing "/" Fails
    Check Stderr Contains  Importing test library 'MyLibDir' failed:  ImportError: No module named MyLibDir

Importing Non Python File Fails
    Check Stderr Contains  Importing test library 'java_libraries.html' failed:  ImportError: No module named java_libraries

Importing Non Python Dir Fails
    Check Stderr Contains  Test library 'library_scope' does not exist.

Importing Non Existing Py File
    Check Stderr Contains  Test library 'this_does_not_exist.py' does not exist.
