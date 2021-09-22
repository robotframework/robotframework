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

Importing By Path Having Spaces
    Check Test Case    ${TEST NAME}

Importing By Path Containing Non-ASCII Characters
    Check Test Case    ${TEST NAME}

Importing Invalid Python File Fails
    ${path} =    Normalize Path    ${DATADIR}/test_libraries/MyInvalidLibFile.py
    Error in file    1    test_libraries/library_import_by_path.robot    9
    ...    Importing library '${path}' failed: ImportError: I'm not really a library!
    ...    traceback=*

Importing Dir Library Without Trailing "/" Fails
    Error in file    0    test_libraries/library_import_by_path.robot    3
    ...    Importing library 'MyLibDir' failed: *Error: *
    ...    traceback=None

Importing Non Python File Fails
    Error in file    2    test_libraries/library_import_by_path.robot    10
    ...    Importing library 'library_import_by_path.robot' failed: *Error: *
    ...    traceback=None

Importing Non Python Dir Fails
    Error in file    3    test_libraries/library_import_by_path.robot    11
    ...    Test library 'library_scope' does not exist.

Importing Non Existing Py File
    Error in file    4    test_libraries/library_import_by_path.robot    13
    ...    Test library 'this_does_not_exist.py' does not exist.

Import failure when path contains non-ASCII characters is handled correctly
    ${path} =    Normalize path    ${DATADIR}/test_libraries/nön_äscii_dïr/invalid.py
    Error in file    -1    test_libraries/library_import_by_path.robot    15
    ...    Importing library '${path}' failed: Ööööps!
    ...    traceback=File "${path}", line 1, in <module>\n*raise RuntimeError('Ööööps!')
