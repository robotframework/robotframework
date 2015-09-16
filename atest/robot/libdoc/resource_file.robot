*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/resource.robot
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be    resource

Documentation
    Doc Should Start With    This resource file has documentation.\n\n
    ...  And it is even set in multiple cells with _formatting_.\n
    ...  This should be in the same paragraph as the sentence above.\n\n
    ...  Here is a literal\nnewline\n\n
    ...  -------------\n\n
    ...  | *TABLE* |\n
    ...  | \${NONEX} | $\{CURDIR} | \${TEMPDIR} |\n
    ...  \n
    ...  tabs \t\t\t here

Version
    Version Should Be    ${EMPTY}

Type
    Type Should Be    resource

Generated
    Generated Should Be Defined

Scope
    Scope Should Be    ${EMPTY}

Named Args
    Named Args Should Be    yes

Resource Has No Inits
    Should Have No Init

Keyword Names
    Keyword Name Should Be     0    curdir
    Keyword Name Should Be     2    Keyword with some "stuff" to <escape>

Keyword Arguments
    Keyword Arguments Should Be     0
    Keyword Arguments Should Be     2    a1    a2
    Keyword Arguments Should Be     5    positional=default    *varargs    **kwargs

Embedded Arguments
    Keyword Name Should Be     1    Embedded \${arguments}
    Keyword Arguments Should Be     1

Keyword Documentation
    Keyword Doc Should Be    0    $\{CURDIR}
    Keyword Doc Should Be    2    foo bar `kw` & some "stuff" to <escape> .\n\n baa `\${a1}`
    Keyword Doc Should Be    4    literal\nnewline
    Keyword Doc Should Be    6
    ...    foo bar `kw`.\n\n
    ...    baa `\${a1}` alskdj alskdjlajd\n
    ...    askf laskdjf asldkfj alsdkfj alsdkfjasldkfj\n
    ...    askf laskdjf _asldkfj_ alsdkfj alsdkfjasldkfj\n
    ...    askf *laskdjf* asldkfj `introduction` alsdkfj\n
    ...    http://foo.bar\n
    ...    - aaa\n
    ...    - bbb\n
    ...    \n
    ...    -------------\n
    ...    \n
    ...    | *1* | *2* |\n
    ...    | foo | bar |
    Keyword Doc Should Be   7
    ...    Summary line\n
    ...    \n
    ...    Another line.

Keyword tags
    Keyword Tags Should Be   4
    Keyword Tags Should Be   5    ?!?!??    Has    kw4    tags
    Keyword Tags Should Be   6    \${3}   a    b
    Keyword Tags Should Be   7    bar    dar    foo

Non ASCII
    Keyword Doc Should Be    8    Hyvää yötä.\n\nСпасибо!
