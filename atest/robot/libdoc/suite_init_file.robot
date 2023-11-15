*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/__init__.robot
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be                    Libdoc

Documentation
    Doc Should Be                     Documentation for keywords in suite ``Libdoc``.

Version
    Version Should Be                 ${EMPTY}

Type
    Type Should Be                    SUITE

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                   GLOBAL

Source Info
    Source Should Be                  ${TESTDATADIR}
    Lineno Should Be                  1

Spec version
    Spec version should be correct

Tags
    Specfile Tags Should Be           $\{CURDIR}    keyword tags    tags

Suite Has No Inits
    Should Have No Init

Keyword Names
    Keyword Name Should Be            0    1. Example
    Keyword Name Should Be            1    2. Keyword with some "stuff" to <escape>

Keyword Arguments
    Keyword Arguments Should Be       0
    Keyword Arguments Should Be       1    a1    a2=c:\\temp\\

Different Argument Types
    Keyword Arguments Should Be       2    mandatory    optional=default    *varargs
    ...                                    kwo=default    another    **kwargs

Embedded Arguments
    Keyword Name Should Be            3    4. Embedded \${arguments}
    Keyword Arguments Should Be       3

Keyword Documentation
    Keyword Doc Should Be             0    Keyword doc with $\{CURDIR}.
    Keyword Doc Should Be             1    foo bar `kw` & some "stuff" to <escape> .\n\nbaa `\${a1}`
    Keyword Doc Should Be             2    Multiple\n\nlines.

Keyword tags
    Keyword Tags Should Be            0    keyword tags    tags
    Keyword Tags Should Be            1    $\{CURDIR}      keyword tags

Non ASCII
    Keyword Doc Should Be             3    Hyvää yötä. дякую!

Keyword Source Info
    Keyword Should Not Have Source    0
    Keyword Lineno Should Be          0    7

Test related settings should not cause errors
    Should Not Contain    ${OUTPUT}    ERROR
