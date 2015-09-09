*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/deprecated_os/files_and_dirs.robot
Force Tags        regression
Resource          atest_resource.robot

*** Test Case ***
Fail Unless Exists
    Check testcase    Fail Unless Exists

Fail Unless Exists With Non Default Message
    Check testcase    Fail Unless Exists With Non Default Message

Fail Unless Exists With Pattern
    Check testcase    Fail Unless Exists With Pattern

Fail If Exists
    Check testcase    Fail If Exists

Fail If Exists With Non Default Message
    Check testcase    Fail If Exists With Non Default Message

Fail If Exists With Pattern
    Check testcase    Fail If Exists With Pattern

Fail Unless File Exists
    Check testcase    Fail Unless File Exists

Fail Unless File Exists When Dir Exists
    Check testcase    Fail Unless File Exists When Dir Exists

Fail Unless File Exists With Non Default Message
    Check testcase    Fail Unless File Exists With Non Default Message

Fail Unless File Exists With Pattern
    Check testcase    Fail Unless File Exists With Pattern

Fail If File Exists
    Check testcase    Fail If File Exists

Fail If File Exists With Non Default Message
    Check testcase    Fail If File Exists With Non Default Message

Fail If File Exists With Pattern Matching One File
    Check testcase    Fail If File Exists With Pattern Matching One File

Fail If File Exists With Pattern Matching Multiple Files
    Check testcase    Fail If File Exists With Pattern Matching Multiple Files

Fail Unless Dir Exists
    Check testcase    Fail Unless Dir Exists

Fail Unless Dir Exists When File Exists
    Check testcase    Fail Unless Dir Exists When File Exists

Fail Unless Dir Exists Exists With Non Default Message
    Check testcase    Fail Unless Dir Exists Exists With Non Default Message

Fail Unless Dir Exists With Pattern
    Check testcase    Fail Unless Dir Exists With Pattern

Fail If Dir Exists
    Check testcase    Fail If Dir Exists

Fail If Dir Exists With Non Default Message
    Check testcase    Fail If Dir Exists With Non Default Message

Fail If Dir Exists With Pattern Matching One Dir
    Check testcase    Fail If Dir Exists With Pattern Matching One Dir

Fail If Dir Exists With Pattern Matching Multiple Dirs
    Check testcase    Fail If Dir Exists With Pattern Matching Multiple Dirs

Fail Unless Dir Empty
    Check testcase    Fail Unless Dir Empty

Fail If Dir Empty
    Check testcase    Fail If Dir Empty

Fail Unless File Empty
    Check testcase    Fail Unless File Empty

Fail If File Empty
    Check testcase    Fail If File Empty

Create Dir
    Check testcase    Create Dir

Creating Dir Over Existing File Fails
    Check testcase    Creating Dir Over Existing File Fails

Remove Dir
    Check testcase    Remove Dir

Remove Dir Recursively
    Check testcase    Remove Dir Recursively

Removing Non-Existing Dir Is Ok
    Check testcase    Removing Non-Existing Dir Is Ok

Removing Non-Empty Dir When Not Recursive Fails
    Check testcase    Removing Non-Empty Dir When Not Recursive Fails

Empty Dir
    Check testcase    Empty Dir

Emptying Non-Existing Dir Fails
    Check testcase    Emptying Non-Existing Dir Fails

Emptying Dir When Dir is File Fails
    Check testcase    Emptying Dir When Dir is File Fails

Move Dir
    Check testcase    Move Dir

Moving Non-Existing Dir Fails
    Check testcase    Moving Non-Existing Dir Fails
