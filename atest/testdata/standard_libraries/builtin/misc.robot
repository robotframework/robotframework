*** Settings ***
Library           Collections

*** Variables ***
@{HELLO}          Hello    world
${TEXT}           foo\nbar\nfoo bar\nFoo

*** Test Cases ***
No Operation
    No Operation

Catenate
    ${str} =    Catenate    Hello    world    !!
    Should Be Equal    ${str}    Hello world !!
    ${str} =    Catenate    SEPARATOR=-    @{HELLO}    !!
    Should Be Equal    ${str}    Hello-world-!!
    ${str} =    Catenate    SEPARATOR=XXX    @{HELLO}    !!
    Should Be Equal    ${str}    HelloXXXworldXXX!!
    ${str} =    Catenate    SEPARATOR=    @{HELLO}    !!
    Should Be Equal    ${str}    Helloworld!!
    ${str} =    Catenate
    Should Be Equal    ${str}    ${EMPTY}
    ${str} =    Catenate    SEPARATOR=xxx
    Should Be Equal    ${str}    ${EMPTY}
    ${str} =    Catenate    Hello
    Should Be Equal    ${str}    Hello
    ${str} =    Catenate    SEPARATOR=xxx    Hello
    Should Be Equal    ${str}    Hello
    ${str} =    Catenate    This    SEPARATOR=won't work
    Should Be Equal    ${str}    This SEPARATOR=won't work
    ${str} =    Catenate    SEPARATOR-This    won't work
    Should Be Equal    ${str}    SEPARATOR-This won't work
    ${str} =    Catenate    separator=This    won't work
    Should Be Equal    ${str}    separator=This won't work

Comment
    Comment    This text is shown    as keyword arguments    but ignored otherwise
    Comment    One message
    Comment
    Comment    Should work also with ${NON EXISTING} variable and ${OTHER NON EXISTING} variable
    Comment    @{NON EXISTING LIST}, &{NONEX DICT} and %{NONEX_ENV_VAR} work too

Regexp Escape
    ${escaped} =    Regexp Escape    f$o^o$b[a]r()?\\
    Should Be Equal    ${escaped}    f\\$o\\^o\\$b\\[a\\]r\\(\\)\\?\\\\
    Should Match Regexp    f$o^o$b[a]r()?\\    ${escaped}
    @{escaped} =    Regexp Escape    $    ^    $    [    ]    so+me&te[]?*x*t
    @{expected} =    Create List    \\$    \\^    \\$    \\[    \\]    so\\+me\\&te\\[\\]\\?\\*x\\*t
    Lists Should Be Equal    ${escaped}    ${expected}
