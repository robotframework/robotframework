*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/deprecated_builtin/misc.robot
Force Tags        regression
Default Tags      jybot    pybot
Resource          atest_resource.robot

*** Test Case ***
Noop
    Check Test Case    Noop

Set
    Check Test Case    Set

Message
    Check Test Case    Message
