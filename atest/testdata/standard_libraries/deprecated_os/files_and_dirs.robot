*** Setting ***
Suite Teardown    Remove Temps
Test Setup        Remove Temps
Library           OperatingSystem

*** Variable ***
${TESTFILE}       ${CURDIR}${/}R-F.txt
${TESTFILE2}      ${CURDIR}${/}R-F2.txt
${TESTFILE3}      ${CURDIR}${/}R-F3.txt
${TESTDIR}        ${CURDIR}${/}R-D
${TESTDIR2}       ${CURDIR}${/}R-D2

*** Test Case ***
Fail Unless Exists
    [Documentation]    FAIL REGEXP: Path '.*non-existing-file-or-dir' does not match any file or directory
    Create File    ${TESTFILE}    whatever
    Fail Unless Exists    ${TESTFILE}
    Fail Unless Exists    ${CURDIR}
    Fail Unless Exists    non-existing-file-or-dir

Fail Unless Exists With Non Default Message
    [Documentation]    FAIL Non-default error message
    Fail Unless Exists    non-existing-file-or-dir    Non-default error message

Fail Unless Exists With Pattern
    [Documentation]    FAIL REGEXP: Path '.*\\*non\\*existing\\*' does not match any file or directory
    Create File    ${TESTFILE}
    Create File    ${TESTFILE2}
    Create Dir    ${TESTDIR}
    Fail Unless Exists    ${CURDIR}${/}*
    Fail Unless Exists    ${CURDIR}${/}*.txt
    Fail Unless Exists    ${CURDIR}${/}R*
    Fail Unless Exists    ${CURDIR}${/}R-?
    Fail Unless Exists    ${CURDIR}${/}[RX]-[ABCD]*
    Fail Unless Exists    *non*existing*

Fail If Exists
    [Documentation]    FAIL Path '${CURDIR}' exists
    Fail If Exists    non-existing-file.txt
    Fail If Exists    ${CURDIR}

Fail If Exists With Non Default Message
    [Documentation]    FAIL This is a non-default error message
    Fail If Exists    ${CURDIR}    This is a non-default error message

Fail If Exists With Pattern
    [Documentation]    FAIL Path '${CURDIR}${/}R-*' matches '${CURDIR}${/}R-D' and '${CURDIR}${/}R-F.txt'
    Fail If Exists    *non?existing*
    Create File    ${TESTFILE}
    Create Dir    ${TESTDIR}
    Fail If Exists    ${CURDIR}${/}R-*

Fail Unless File Exists
    [Documentation]    FAIL REGEXP: Path '.*non-existing-file' does not match any file
    Create File    ${TESTFILE}    whatever
    Fail Unless File Exists    ${TESTFILE}
    Fail Unless File Exists    non-existing-file

Fail Unless File Exists When Dir Exists
    [Documentation]    FAIL Path '${CURDIR}' does not match any file
    Fail Unless File Exists    ${CURDIR}

Fail Unless File Exists With Non Default Message
    [Documentation]    FAIL Hello, this is a non-default error
    Fail Unless File Exists    ${CURDIR}    Hello, this is a non-default error

Fail Unless File Exists With Pattern
    [Documentation]    FAIL Path '${CURDIR}${/}robot_temp_d??' does not match any file
    Create File    ${TESTFILE}    whatever
    Create Dir    ${TESTDIR}
    Fail Unless File Exists    ${CURDIR}${/}R-*
    Fail Unless File Exists    ${CURDIR}${/}R[!abcd][FD].t?t
    Fail Unless File Exists    ${CURDIR}${/}robot_temp_d??

Fail If File Exists
    [Documentation]    FAIL File '${TESTFILE}' exists
    Create File    ${TESTFILE}    whatever
    Fail If File Exists    non-existing-file.txt
    Fail If File Exists    ${CURDIR}
    Fail If File Exists    ${TESTFILE}

Fail If File Exists With Non Default Message
    [Documentation]    FAIL My non-default
    Create File    ${TESTFILE}    whatever
    Fail If File Exists    ${TESTFILE}    My non-default

Fail If File Exists With Pattern Matching One File
    [Documentation]    FAIL Path '${CURDIR}${/}R-*.txt' matches file '${CURDIR}${/}R-F.txt'
    Create File    ${TESTFILE}    whatever
    Create Dir    ${TESTDIR}
    Fail If File Exists    *non?existing*
    Fail If File Exists    ${CURDIR}${/}R-D
    Fail If File Exists    ${CURDIR}${/}R-*.txt

Fail If File Exists With Pattern Matching Multiple Files
    [Documentation]    FAIL Path '${CURDIR}${/}R-*.txt' matches files '${CURDIR}${/}R-F.txt' and '${CURDIR}${/}R-F2.txt'
    Create File    ${TESTFILE}    whatever
    Create File    ${TESTFILE2}    whatever
    Fail If File Exists    ${CURDIR}${/}R-*.txt

Fail Unless Dir Exists
    [Documentation]    Normal ok cases and failure with default message when dir doesn't exists FAIL REGEXP: Path '.*non-existing-directory' does not match any directory
    Fail Unless Dir Exists    ${TEMPDIR}
    Fail Unless Dir Exists    non-existing-directory

Fail Unless Dir Exists When File Exists
    [Documentation]    FAIL Path '${TESTFILE}' does not match any directory
    Create File    ${TESTFILE}
    Fail Unless Dir Exists    ${TESTFILE}

Fail Unless Dir Exists Exists With Non Default Message
    [Documentation]    FAIL One more non-default error
    Fail Unless Dir Exists    non-existing-directory    One more non-default error

Fail Unless Dir Exists With Pattern
    [Documentation]    FAIL Path '${CURDIR}${/}R-F.txt' does not match any directory
    Create File    ${TESTFILE}
    Create Dir    ${TESTDIR}
    Fail Unless Dir Exists    ${CURDIR}${/}R-*
    Fail Unless Dir Exists    ${CURDIR}${/}R[!whatever][DB]*
    Fail Unless Dir Exists    ${CURDIR}${/}R-F.txt

Fail If Dir Exists
    [Documentation]    FAIL Directory '${CURDIR}' exists
    Create File    ${TESTFILE}
    Fail If Dir Exists    non-existing
    Fail If Dir Exists    ${TESTFILE}
    Fail If Dir Exists    ${CURDIR}

Fail If Dir Exists With Non Default Message
    [Documentation]    FAIL Still one more non-default msg
    Fail If Dir Exists    ${CURDIR}    Still one more non-default msg

Fail If Dir Exists With Pattern Matching One Dir
    [Documentation]    FAIL Path '${CURDIR}${/}R-*' matches directory '${TESTDIR}'
    Create File    ${TESTFILE}
    Create Dir    ${TESTDIR}
    Fail If Dir Exists    *non?existing*
    Fail If Dir Exists    ${CURDIR}${/}R-F.txt
    Fail If Dir Exists    ${CURDIR}${/}R-*

Fail If Dir Exists With Pattern Matching Multiple Dirs
    [Documentation]    FAIL Path '${CURDIR}${/}R-[DF]*' matches directories '${TESTDIR}' and '${TESTDIR2}'
    Create Dir    ${TESTDIR}
    Create Dir    ${TESTDIR2}
    Fail If Dir Exists    ${CURDIR}${/}R-[DF]*

Fail Unless Dir Empty
    [Documentation]    FAIL Directory '${TESTDIR}' is not empty. Contents: 'f1.txt', 'f2.txt', 'f3.txt'
    Create Dir    ${TESTDIR}
    Fail Unless Dir Empty    ${TESTDIR}
    Create File    ${TESTDIR}${/}f1.txt
    Create File    ${TESTDIR}${/}f2.txt
    Create File    ${TESTDIR}${/}f3.txt
    Fail Unless Dir Empty    ${TESTDIR}    # Fails

Fail If Dir Empty
    [Documentation]    FAIL Directory '${TESTDIR}' is empty.
    Create Dir    ${TESTDIR}
    Create File    ${TESTDIR}${/}file.txt
    Fail If Dir Empty    ${TESTDIR}
    Remove File    ${TESTDIR}${/}file.txt
    Fail If Dir Empty    ${TESTDIR}    # Fails

Fail Unless File Empty
    [Documentation]    FAIL File '${TESTFILE}' is not empty. Size: 12 bytes
    Create File    ${TESTFILE}
    Fail Unless File Empty    ${TESTFILE}
    Create File    ${TESTFILE}    some content
    Fail Unless File Empty    ${TESTFILE}

Fail If File Empty
    [Documentation]    FAIL File '${TESTFILE}' is empty.
    Create File    ${TESTFILE}    some content
    Fail If File Empty    ${TESTFILE}
    Create File    ${TESTFILE}
    Fail If File Empty    ${TESTFILE}

Create Dir
    Create Dir    ${TESTDIR}
    Fail Unless Dir Exists    ${TESTDIR}
    Create Dir    ${TESTDIR}
    Create Dir    ${TESTDIR}${/}sub${/}dirs${/}here
    Fail Unless Dir Exists    ${TESTDIR}${/}sub${/}dirs${/}here

Creating Dir Over existing File Fails
    [Documentation]    FAIL Path '${TESTFILE}' already exists but is not a directory
    Create File    ${TESTFILE}
    Create Dir    ${TESTFILE}

Remove Dir
    Create Dir    ${TESTDIR}
    Remove Dir    ${TESTDIR}
    Fail If Exists    ${TESTDIR}

Remove Dir Recursively
    Create Dir    ${TESTDIR}${/}sub
    Create File    ${TESTDIR}${/}file.txt
    Create File    ${TESTDIR}${/}sub${/}file2.txt
    Remove Dir    ${TESTDIR}    Recursive
    Fail If Exists    ${TESTDIR}

Removing Non-Existing Dir Is Ok
    Remove Dir    non-existing-dir

Removing Non-Empty Dir when not Recursive Fails
    [Documentation]    FAIL Directory '${TESTDIR}' is not empty.
    Create Dir    ${TESTDIR}
    Create File    ${TESTDIR}${/}file.txt
    Remove Dir    ${TESTDIR}

Empty Dir
    Create Dir    ${TESTDIR}
    Create File    ${TESTDIR}${/}foo.txt
    Create File    ${TESTDIR}${/}bar.txt
    Create Dir    ${TESTDIR}${/}subdir
    Create File    ${TESTDIR}${/}subdir${/}sub.txt
    Fail If Dir Empty    ${TESTDIR}
    Empty Dir    ${TESTDIR}
    Fail Unless Dir Empty    ${TESTDIR}

Emptying Non-Existing Dir Fails
    [Documentation]    FAIL Directory '${CURDIR}${/}nonexisting' does not exist
    Empty Dir    ${CURDIR}${/}nonexisting

Emptying Dir When Dir is File Fails
    [Documentation]    FAIL Directory '${TESTFILE}' does not exist
    Create File    ${TESTFILE}
    Empty Dir    ${TESTFILE}

Move Dir
    [Documentation]    Moving directory around. Moving to excisting and non-existing directory should pass. PASS
    Create Dir    ${TESTDIR}${/}sub
    Create File    ${TESTDIR}${/}world.txt    world
    Create File    ${TESTDIR}${/}tellus.txt    tellus
    Create File    ${TESTDIR}${/}sub${/}marine.txt    sub\nmarine
    # Move to new dir (same as rename)
    Move Dir    ${TESTDIR}    ${TESTDIR2}${/}foo
    Fail If Exists    ${TESTDIR}
    Get and Check File    ${TESTDIR2}${/}foo${/}world.txt    world
    Get and Check File    ${TESTDIR2}${/}foo${/}tellus.txt    tellus
    Get and Check File    ${TESTDIR2}${/}foo${/}sub${/}marine.txt    sub\nmarine
    # Move to existing dir
    Create Dir    ${TESTDIR}
    Move Dir    ${TESTDIR2}${/}foo    ${TESTDIR}
    Fail If Exists    ${TESTDIR2}${/}foo
    Get and Check File    ${TESTDIR}${/}foo${/}world.txt    world
    Get and Check File    ${TESTDIR}${/}foo${/}tellus.txt    tellus
    Get and Check File    ${TESTDIR}${/}foo${/}sub${/}marine.txt    sub\nmarine
    # Move to non-existing with missing intermediate dirs
    Move Dir    ${TESTDIR}${/}foo    ${TESTDIR2}${/}foo${/}bar
    Fail If Exists    ${TESTDIR}${/}foo
    Get and Check File    ${TESTDIR2}${/}foo${/}bar${/}world.txt    world
    Get and Check File    ${TESTDIR2}${/}foo${/}bar${/}tellus.txt    tellus
    Get and Check File    ${TESTDIR2}${/}foo${/}bar${/}sub${/}marine.txt    sub\nmarine

Moving Non-Existing Dir Fails
    [Documentation]    FAIL Source directory '${CURDIR}${/}non-existing-dir' does not exist
    Move Dir    ${CURDIR}${/}non-existing-dir    whatever

*** Keyword ***
Get And Check File
    [Arguments]    ${path}    ${expected}
    ${content}    Get File    ${path}
    Fail Unless Equal    ${content}    ${expected}

Remove Temps
    Remove Files    ${TESTFILE}    ${TESTFILE2}
    Remove Dir    ${TESTDIR}    recursive
    Remove Dir    ${TESTDIR2}    recursive

Sleep And Remove File And Dir
    [Arguments]    ${path_to_file}    ${path_to_dir}
    Sleep    1s 500 ms
    Remove File    ${path_to_file}
    Remove Dir    ${path_to_dir}

Sleep And Create File And Dir
    [Arguments]    ${path_to_file}    ${path_to_dir}
    Sleep    1s 500 ms
    Create File    ${path_to_file}
    Create Dir    ${path_to_dir}
