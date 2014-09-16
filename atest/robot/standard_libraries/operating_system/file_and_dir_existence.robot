*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/operating_system/file_and_dir_existence.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***
Should Exist
    Check testcase  Should Exist

Should Exist With Non Default Message
    Check testcase  Should Exist With Non Default Message

Should Exist With Pattern
    Check testcase  Should Exist With Pattern

Should Not Exist
    Check testcase  Should Not Exist

Should Not Exist With Non Default Message
    Check testcase  Should Not Exist With Non Default Message

Should Not Exist With Pattern
    Check testcase  Should Not Exist With Pattern

File Should Exist
    Check testcase  File Should Exist

File Should Exist When Dir Exists
    Check testcase  File Should Exist When Dir Exists

File Should Exist With Non Default Message
    Check testcase  File Should Exist With Non Default Message

File Should Exist With Pattern
    Check testcase  File Should Exist With Pattern

File Should Not Exist
    Check testcase  File Should Not Exist

File Should Not Exist With Non Default Message
    Check testcase  File Should Not Exist With Non Default Message

File Should Not Exist With Pattern Matching One File
    Check testcase  File Should Not Exist With Pattern Matching One File

File Should Not Exist With Pattern Matching Multiple Files
    Check testcase  File Should Not Exist With Pattern Matching Multiple Files

Directory Should Exist
    Check testcase  Directory Should Exist

Directory Should Exist When File Exists
    Check testcase  Directory Should Exist When File Exists

Directory Should Exist Exists With Non Default Message
    Check testcase  Directory Should Exist Exists With Non Default Message

Directory Should Exist With Pattern
    Check testcase  Directory Should Exist With Pattern

Directory Should Not Exist
    Check testcase  Directory Should Not Exist

Directory Should Not Exist With Non Default Message
    Check testcase  Directory Should Not Exist With Non Default Message

Directory Should Not Exist With Pattern Matching One Dir
    Check testcase  Directory Should Not Exist With Pattern Matching One Dir

Directory Should Not Exist With Pattern Matching Multiple Dirs
    Check testcase  Directory Should Not Exist With Pattern Matching Multiple Dirs

