*** Settings ***
Library           MyLibFile.py
Library           MyLibDir
Library           MyLibDir/
Library           dir_for_libs/MyLibFile2.py
Library           dir_for_libs/lib1/Lib.py    WITH NAME    lib1
Library           dir_for_libs/lib2/Lib.py    WITH NAME    lib2
Library           ${MYVAR}/MyLibDir2/
Library           MyInvalidLibFile.py
Library           library_import_by_path.robot
Library           library_scope/
Library           spaces in path/SpacePathLib.py
Library           this_does_not_exist.py
Library           nön_äscii_dïr/valid.py
Library           nön_äscii_dïr/invalid.py

*** Variables ***
${MYVAR}          ${CURDIR}${/}dir_for_libs

*** Test Cases ***
Importing Python Library In File By Path
    Keyword In My Lib File
    ${ret} =    Keyword In My Lib File 2    world
    Should Be Equal    ${ret}    Hello world!

Importing Python Library In Dir By Path
    ${ret} =    MyLibDir.Keyword In My Lib Dir
    Should Be Equal    ${ret}    Executed keyword 'Keyword In My Lib Dir' with args [ ]
    ${ret} =    Keyword In My Lib Dir    a1    a2
    Should Be Equal    ${ret}    Executed keyword 'Keyword In My Lib Dir' with args [ a1 | a2 ]

Importing Library With Same Name
    lib1.Hello
    lib2.Hello
    Kw from lib1
    Kw from lib2

Importing Python Library By Path With Variables
    ${sum} =    Keyword In My Lib Dir 2    1    2    3    4    5
    Should Be Equal    ${sum}    ${15}

Importing By Path Having Spaces
    ${ret} =    Spaces in Library Path
    Should Be Equal    ${ret}    here was a bug

Importing By Path Containing Non-ASCII Characters
    ${ret} =    Keyword in non ASCII dir
    Should Be Equal    ${ret}    Keyword in 'nön_äscii_dïr'!
