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
    ...    | foo | bar |
    ...    tabs \t\t\t here

Version
    Version Should Be               ${EMPTY}

Type
    Type Should Be                  resource

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                 ${EMPTY}

Named Args
    Named Args Should Be            yes

Resource Has No Inits
    Should Have No Init

Keyword Names
    Keyword Name Should Be          0    curdir
    Keyword Name Should Be          3    Keyword with some "stuff" to <escape>

Keyword Arguments
    Keyword Arguments Should Be     0
    Keyword Arguments Should Be     3    a1    a2
    Keyword Arguments Should Be     6    positional=default    *varargs    **kwargs

Different Argument Types
    Keyword Arguments Should Be     1    mandatory    optional=default    *varargs
    ...                                  kwo=default    another    **kwargs

Embedded Arguments
    Keyword Name Should Be          2    Embedded \${arguments}
    Keyword Arguments Should Be     2

Keyword Documentation
    Keyword Doc Should Be           0    $\{CURDIR}
    Keyword Doc Should Be           3    foo bar `kw` & some "stuff" to <escape> .\n\nbaa `\${a1}`
    Keyword Doc Should Be           5    literal\nnewline
    Keyword Doc Should Be           7
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
    ...    | foo | bar |
    Keyword Doc Should Be           8
    ...    Summary line
    ...
    ...    Another line.

Keyword tags
    Keyword Tags Should Be          5
    Keyword Tags Should Be          6    ?!?!??    Has    kw4    tags
    Keyword Tags Should Be          7    \${3}   a    b
    Keyword Tags Should Be          8    bar    dar    foo

Non ASCII
    Keyword Doc Should Be           9    Hyvää yötä.\n\nСпасибо!

'*.resource' extension is accepted
    Run Libdoc And Parse Output     ${TESTDATADIR}/resource.resource
    Keyword Name Should Be          0    Yay, I got new extension!
    Keyword Arguments Should Be     0    Awesome!!
    Keyword Doc Should Be           0    Yeah!!!
