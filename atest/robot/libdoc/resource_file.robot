*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/resource.robot
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be                  resource

Documentation
    Doc Should Be
    ...    This resource file has documentation.
    ...
    ...    And it is even set in multiple cells with _formatting_.
    ...    This should be in the same paragraph as the sentence above.
    ...
    ...    Here is a literal\nnewline
    ...
    ...    -------------
    ...
    ...    | *TABLE* |
    ...    | \${NONEX} | $\{CURDIR} | \${TEMPDIR} |
    ...    | foo${SPACE*6}|${SPACE*4}bar${SPACE*4}|
    ...    tabs \t\t\t here

Version
    Version Should Be               ${EMPTY}

Type
    Type Should Be                  RESOURCE

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                 GLOBAL

Source Info
    Source Should Be                ${TESTDATADIR}/resource.robot
    Lineno Should Be                1

Spec version
    Spec version should be correct

Resource Tags
    Specfile Tags Should Be          \${3}    ?!?!??    a      b    bar    dar
    ...                              foo      Has       kw4    robot:private    tags

Resource Has No Inits
    Should Have No Init

Keyword Names
    Keyword Name Should Be          0    curdir
    Keyword Name Should Be          4    Keyword with some "stuff" to <escape>

Keyword Arguments
    Keyword Arguments Should Be     0
    Keyword Arguments Should Be     4    a1    a2
    Keyword Arguments Should Be     7    positional=default    *varargs    **kwargs

Different Argument Types
    Keyword Arguments Should Be     2    mandatory    optional=default    *varargs
    ...                                  kwo=default    another    **kwargs

Embedded Arguments
    Keyword Name Should Be          3    Embedded \${arguments}
    Keyword Arguments Should Be     3

Keyword Documentation
    Keyword Doc Should Be           0    $\{CURDIR}
    Keyword Doc Should Be           4    foo bar `kw` & some "stuff" to <escape> .\n\nbaa `\${a1}`
    Keyword Doc Should Be           6    literal\nnewline
    Keyword Doc Should Be           8
    ...    foo bar `kw`.
    ...
    ...    FIRST `\${a1}` alskdj alskdjlajd
    ...    askf laskdjf asldkfj alsdkfj alsdkfjasldkfj END
    ...
    ...    SECOND askf laskdjf _asldkfj_ alsdkfj alsdkfjasldkfj
    ...    askf *laskdjf* END
    ...
    ...    THIRD asldkfj `introduction` alsdkfj http://foo.bar END
    ...    - aaa
    ...    - bbb
    ...
    ...    -------------
    ...
    ...    | = first = | = second = |
    ...    | foo${SPACE*7}|${SPACE*4}bar${SPACE*5}|
    Keyword Doc Should Be           9
    ...    Summary line
    ...
    ...    Another line.

Deprecation
    Keyword Doc Should Be           1    *DEPRECATED* for some reason.
    Keyword Should Be Deprecated    1
    FOR    ${index}    IN RANGE    2    11
        Keyword Should Not Be Deprecated    ${index}
    END

Keyword tags
    Keyword Tags Should Be          6
    Keyword Tags Should Be          7    ?!?!??    Has    kw4    tags
    Keyword Tags Should Be          8    \${3}   a    b
    Keyword Tags Should Be          9    bar    dar    foo

Non ASCII
    Keyword Doc Should Be           10    Hyvää yötä.\n\nСпасибо!

Keyword Source Info
    Keyword Name Should Be            0    curdir
    Keyword Should Not Have Source    0
    Keyword Lineno Should Be          0    71

'*.resource' extension is accepted
    Run Libdoc And Parse Output       ${TESTDATADIR}/resource.resource
    Source Should Be                  ${TESTDATADIR}/resource.resource
    Lineno Should Be                  1
    Keyword Name Should Be            2    Yay, I got new extension!
    Keyword Arguments Should Be       2    Awesome!!
    Keyword Doc Should Be             2    Yeah!!!
    Keyword Should Not Have Source    2
    Keyword Lineno Should Be          2    5

Keyword Tags setting
    Keyword Tags Should Be            0    keyword    own    tags
    Keyword Tags Should Be            1    in doc    keyword    own    tags
    Keyword Tags Should Be            2    keyword    tags
