*** Settings ***
Documentation     Importing test libraries using relative and absolute path.
Suite Setup       Run Tests    ${EMPTY}    test_libraries/library_import_by_path.robot
Resource          atest_resource.robot

*** Test Cases ***
Importing Python Library In File By Path
    ${test} =    Check Test Case    Importing Python Library In File By Path
    Check Keyword Data    ${test.kws[0]}    MyLibFile.Keyword In My Lib File
    Check Keyword Data    ${test.kws[1]}    MyLibFile2.Keyword In My Lib File 2    \${ret}    world

Importing Python Library In Dir By Path
    ${test} =    Check Test Case    Importing Python Library In Dir By Path
    Check Keyword Data    ${test.kws[0]}    MyLibDir.Keyword In My Lib Dir    \${ret}
    Check Keyword Data    ${test.kws[2]}    MyLibDir.Keyword In My Lib Dir    \${ret}    a1, a2

Importing Library With Same Name
    ${tc} =    Check Test Case    ${TEST NAME}
    Check log message    ${tc.kws[0].msgs[0]}    Hello from lib1
    Check log message    ${tc.kws[1].msgs[0]}    Hello from lib2

Importing Python Library By Path With Variables
    ${test} =    Check Test Case    Importing Python Library By Path With Variables
    Check Keyword Data    ${test.kws[0]}    MyLibDir2.Keyword In My Lib Dir 2    \${sum}    1, 2, 3, 4, 5

Importing Java Library File By Path With .java Extension
    [Tags]    require-jython
    ${test} =    Check Test Case    Importing Java Library File By Path With .java Extension
    Check Keyword Data    ${test.kws[0]}    MyJavaLib.Keyword In My Java Lib    \${ret}    tellus

Importing Java Library File By Path With .class Extension
    [Tags]    require-jython
    ${test} =    Check Test Case    Importing Java Library File By Path With .class Extension
    Check Keyword Data    ${test.kws[0]}    MyJavaLib2.Keyword In My Java Lib 2    \${ret}    maailma

Importing By Path Having Spaces
    Check Test Case    Importing By Path Having Spaces

Importing Invalid Python File Fails
    ${path} =    Normalize Path    ${DATADIR}/test_libraries/MyInvalidLibFile.py
    Check Stderr Contains    Importing test library '${path}' failed: ImportError: I'm not really a library!

Importing Dir Library Without Trailing "/" Fails
    Check Stderr Contains    Importing test library 'MyLibDir' failed: ImportError:

Importing Non Python File Fails
    Check Stderr Contains    Importing test library 'library_import_by_path.robot' failed: ImportError:

Importing Non Python Dir Fails
    Check Stderr Contains    Test library 'library_scope' does not exist.

Importing Non Existing Py File
    Check Stderr Contains    Test library 'this_does_not_exist.py' does not exist.
