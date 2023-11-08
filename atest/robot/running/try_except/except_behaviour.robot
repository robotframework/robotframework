*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/except_behaviour.robot
Test Template     Verify try except and block statuses

*** Test Cases ***
Equals is the default matcher
    FAIL    PASS               pattern_types=[None]

Equals with whitespace
    FAIL    PASS

Glob matcher
    FAIL    NOT RUN    PASS    pattern_types=['GloB', 'gloB']

Startswith matcher
    FAIL    PASS               pattern_types=['start']

Regexp matcher
    FAIL    NOT RUN    PASS    pattern_types=['REGEXP', 'REGEXP']

Regexp escapes
    FAIL    PASS

Regexp flags
    FAIL    NOT RUN    PASS

Variable in pattern
    FAIL    PASS

Invalid variable in pattern
    FAIL    FAIL    PASS

Non-string pattern
    FAIL    NOT RUN    NOT RUN    NOT RUN    NOT RUN

Variable in pattern type
    FAIL    PASS                  pattern_types=['\${regexp}']

Invalid variable in pattern type
    FAIL    FAIL    PASS          pattern_types=['\${does not exist}']

Invalid pattern type
    FAIL    NOT RUN    NOT RUN    pattern_types=['glob', 'invalid']

Invalid pattern type from variable
    FAIL    FAIL                  pattern_types=["\${{'invalid'}}"]

Non-string pattern type
    FAIL    FAIL                  pattern_types=['\${42}']

Pattern type multiple times
    FAIL    PASS    NOT RUN       pattern_types=['start']

Pattern type without patterns
    FAIL    PASS

Skip cannot be caught
    SKIP    NOT RUN    PASS    tc_status=SKIP

Return cannot be caught
    PASS    NOT RUN    PASS    path=body[0].body[0]

AS gets the message
    FAIL    PASS

AS with multiple pattern
    FAIL    PASS

AS with many failures
    FAIL    PASS

AS with default except
    FAIL    PASS

AS as the error message
    FAIL    PASS
