*** Settings ***
Library           OperatingSystem

*** Test Cases ***
Join Path
    Join Path And Check    abc    abc
    Join Path And Check    abc${/}123    abc    123
    Join Path And Check    abc${/}123    abc${/}    123${/}
    Join Path And Check    a${/}b${/}c${/}d${/}e    a    b    c    d${/}e
    Join Path And Check    ${CURDIR}    ${CURDIR}
    Join Path And Check    ${CURDIR}${/}foo    ${CURDIR}    foo
    Join Path And Check    ${CURDIR}${/}bar    %{TEMPDIR}    ${CURDIR}    bar

Join Paths
    @{paths} =    Join Paths    base    example    other
    Should Be Equal    ${paths}[0]    base${/}example
    Should Be Equal    ${paths}[1]    base${/}other
    Length Should Be    ${paths}    2
    @{paths} =    Join Paths    ${CURDIR}${/}my${/}base    %{TEMPDIR}${/}example    other
    Should Be Equal    ${paths}[0]    %{TEMPDIR}${/}example
    Should Be Equal    ${paths}[1]    ${CURDIR}${/}my${/}base${/}other
    Length Should Be    ${paths}    2
    @{paths} =    Join Paths    my${/}base    example${/}path${/}    other    one${/}more
    Should Be Equal    ${paths}[0]    my${/}base${/}example${/}path
    Should Be Equal    ${paths}[1]    my${/}base${/}other
    Should Be Equal    ${paths}[2]    my${/}base${/}one${/}more
    Length Should Be    ${paths}    3

Normalize Path
    Normalize Path And Check    abc    abc
    Normalize Path And Check    abc${/}def    abc${/}def
    Normalize Path And Check    .    .
    Normalize Path And Check    abc${/}    abc
    Normalize Path And Check    abc${/}..${/}def    def
    Normalize Path And Check    abc${/}..${/}def${/}..${/}ghi    ghi
    Normalize Path And Check    abc${/}def${/}..${/}..${/}ghi    ghi
    Normalize Path And Check    abc${/}..    .
    Normalize Path And Check    abc${/}..${/}    .
    Normalize Path And Check    abc${/}.    abc
    Normalize Path And Check    abc${/}.${/}    abc
    Normalize Path And Check    ..    ..
    Normalize Path And Check    ..${/}abc    ..${/}abc
    Normalize Path And Check    abc${/}${/}def    abc${/}def
    Normalize Path And Check    abc${/ * 10}def    abc${/}def
    Normalize Path And Check    ${CURDIR}${/}${/}abc${/}.${/}..${/}.${/}${/}    ${CURDIR}

Case Normalize Path On Windows
    Normalize Path And Check    ABC        abc         case_normalize=True
    Normalize Path And Check    ABC/DeF    abc\\def    case_normalize=YES
    Normalize Path And Check    ABC        ABC         case_normalize=False
    Normalize Path And Check    ABC/DeF    ABC\\DeF    case_normalize=OFF

Case Normalize Path Outside Windows
    Normalize Path And Check    ABC        ABC        case_normalize=True
    Normalize Path And Check    ABC/DeF    ABC/DeF    case_normalize=YES
    Normalize Path And Check    ABC        ABC        case_normalize=False
    Normalize Path And Check    ABC/DeF    ABC/DeF    case_normalize=OFF

Split Path
    Split Path And Check    abc${/}def    abc    def
    Split Path And Check    abc${/}def${/}ghi${/}    abc${/}def    ghi
    Split Path And Check    abc${/}..${/}def${/}.${/}${/}ghi    def    ghi
    Split Path And Check    abc${/}    ${EMPTY}    abc
    Split Path And Check    abc    ${EMPTY}    abc
    Split Path And Check    ${CURDIR}${/}abc    ${CURDIR}    abc
    Split Path And Check    ..${/}abc    ..    abc
    Split Path And Check    ..    ${EMPTY}    ..

Split Extension
    Split Extension And Check    abc.ext    abc    ext
    Split Extension And Check    abc    abc    ${EMPTY}
    Split Extension And Check    abc.    abc.    ${EMPTY}
    Split Extension And Check    abc.ext.    abc    ext.
    Split Extension And Check    abc...ext...    abc..    ext...
    Split Extension And Check    .abc    .abc    ${EMPTY}
    Split Extension And Check    .abc.ext    .abc    ext
    Split Extension And Check    ..abc.ext    ..abc    ext
    Split Extension And Check    ...abc....ext...    ...abc...    ext...
    Split Extension And Check    abc.def.extension    abc.def    extension
    Split Extension And Check    .abc.def.extension    .abc.def    extension
    Split Extension And Check    path/abc.ext    path${/}abc    ext
    Split Extension And Check    ${CURDIR}/path${/}abc.ext2    ${CURDIR}${/}path${/}abc    ext2
    Split Extension And Check    path${/}..${/}abc.e_x_t    abc    e_x_t
    Split Extension And Check    p1${/}..${/}p2${/}/    p2    ${EMPTY}
    Split Extension And Check    p1${/}..${/}p2${/}${/}${/}abc.ext    p2${/}abc    ext
    Split Extension And Check    path/.file.ext    path${/}.file    ext
    Split Extension And Check    path/.file    path${/}.file    ${EMPTY}
    Split Extension And Check    path/...file.ext    path${/}...file    ext
    Split Extension And Check    path/...file    path${/}...file    ${EMPTY}
    Split Extension And Check    path/file.ext.    path${/}file    ext.
    Split Extension And Check    path/file.ext...    path${/}file    ext...
    Split Extension And Check    path/...file..ext...    path${/}...file.    ext...

Forward Slash Works as Separator On All OSes
    Join Path And Check    a${/}b${/}c${/}d${/}e${/}f${/}g    a/b    c/d${/}e    f/g
    Normalize Path And Check    foo/bar/../zap    foo${/}zap
    Split Path And Check    foo/bar/zap    foo${/}bar    zap
    Split Extension And Check    foo/bar/zap.txt    foo${/}bar${/}zap    txt

Non-ASCII
    Join Path And Check    ñõñ${/}âŝĉîî    ñõñ    âŝĉîî
    Normalize Path And Check    ñõñ/.${/}âŝĉîî${/}    ñõñ${/}âŝĉîî
    Split Path And Check    ñõñ/âŝĉîî    ñõñ    âŝĉîî
    Split Extension And Check    ñõñ/âŝĉîî.åäö    ñõñ${/}âŝĉîî    åäö

With Space
    Join Path And Check    with space${/}and another    with space    and another
    Normalize Path And Check    with space/./and another/.    with space${/}and another
    Split Path And Check    with space/and another    with space    and another
    Split Extension And Check    with space.and another    with space    and another

Path as `pathlib.Path`
    Join Path And Check    foo${/}bar    ${{pathlib.Path('foo')}}    ${{pathlib.Path('bar')}}
    Normalize Path And Check     ${{pathlib.Path('foo/../bar')}}    bar
    Split Path And Check         ${{pathlib.Path('foo/bar')}}       foo    bar
    Split Extension And Check    ${{pathlib.Path('foo.bar')}}       foo    bar

*** Keywords ***
Join Path And Check
    [Arguments]    ${expected}    @{inputs}
    ${path} =    Join Path    @{inputs}
    Should Be Equal    ${path}    ${expected}    Joining ${inputs} failed

Normalize Path And Check
    [Arguments]    ${input}    ${expected}    &{config}
    ${path} =    Normalize Path    ${input}    &{config}
    Should Be Equal    ${path}    ${expected}    Normalizing ${input} failed

Split Path And Check
    [Arguments]    ${input}    ${exp1}    ${exp2}
    ${out1}    ${out2} =    Split Path    ${input}
    Should Be Equal    ${out1}    ${exp1}    Splitting path ${input} failed
    Should Be Equal    ${out2}    ${exp2}    Splitting path ${input} failed

Split Extension And Check
    [Arguments]    ${input}    ${exp1}    ${exp2}
    ${out1}    ${out2}    Split Extension    ${input}
    Should Be Equal    ${out1}    ${exp1}    Splitting extension from ${input} failed
    Should Be Equal    ${out2}    ${exp2}    Splitting extension from ${input} failed
