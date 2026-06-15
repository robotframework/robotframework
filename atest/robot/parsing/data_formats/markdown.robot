*** Settings ***
Resource        formats_resource.robot

*** Test Cases ***
One Markdown file
    Run Sample File And Check Tests    ${EMPTY}    ${MARKDOWN DIR}/sample.md

Markdown With Markdown Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

Parsing errors have correct source
    Previous Run Should Have Been Successful
    Error in file    0    ${MARKDOWN DIR}/sample.md    10
    ...    Non-existing setting 'Invalid'.
    Error in file    1    ${MARKDOWN DIR}/../resources/markdown_resource.md    2
    ...    Non-existing setting 'Invalid Resource'.
    Length should be    ${ERRORS}    2

Markdown Directory
    Run Tests    -F md:markdown    ${MARKDOWN DIR}
    Should Be Equal    ${SUITE.name}    Markdown
    Should Contain Suites    ${SUITE}    Sample    With Init
    Should Contain Suites    ${SUITE.suites[1]}    Fence Blocks    Sub Suite1    Sub Suite2
    Should Contain Tests    ${SUITE}    @{SAMPLE_TESTS}    @{SUBSUITE_TESTS}    Tilde Fence    Longer Closure Fence    Info String
    ${path} =    Normalize Path    ${MARKDOWN DIR}
    Syslog Should Contain    | INFO \ | Data source '${path}${/}invalid.markdown' has no tests or tasks.
    Syslog Should Contain    | INFO \ | Data source '${path}${/}empty.markdown' has no tests or tasks.
    Syslog Should Contain    | INFO \ | Ignoring file or directory '${path}${/}not_a_picture.jpg'.

Directory With Markdown Init
    Previous Run Should Have Been Successful
    ${suite} =    Set Variable    ${SUITE.suites[1]}
    Should Be Equal    ${suite.name}    With Init
    Should Be Equal    ${suite.doc}    Testing suite init file
    Check Log Message    ${suite.setup[0].messages[0]}    Running suite setup
    Teardown Should Not Be Defined    ${suite}
    Should Contain Suites    ${suite}    Fence Blocks    Sub Suite1    Sub Suite2
    Should Contain Tests    ${suite}    @{SUBSUITE_TESTS}    Tilde Fence    Longer Closure Fence    Info String

Parsing errors in init file have correct source
    Previous Run Should Have Been Successful
    Error in file    0    ${MARKDOWN DIR}/sample.md    10
    ...    Non-existing setting 'Invalid'.
    Error in file    1    ${MARKDOWN DIR}/with_init/__init__.md    4
    ...    Non-existing setting 'Invalid Init'.
    Error in file    2    ${MARKDOWN DIR}/../resources/markdown_resource.md    2
    ...    Non-existing setting 'Invalid Resource'.
    Length should be    ${ERRORS}    3

Fence Block Parsing In Markdown
    Run Tests    ${EMPTY}    ${MARKDOWN DIR}/with_init/fence_blocks.md
    Should Be Equal    ${SUITE.name}    Fence Blocks
    Should Contain Tests    ${SUITE}    Tilde Fence    Longer Closure Fence    Info String
    Length Should Be    ${SUITE.tests}    3

'.robot.md' files are parsed automatically
    Run Tests    ${EMPTY}    ${MARKDOWN DIR}/with_init
    Should Be Equal    ${SUITE.name}    With Init
    Should Be Equal    ${SUITE.suites[0].name}    Sub Suite2
    Should Contain Tests    ${SUITE}    Suite2 Test
