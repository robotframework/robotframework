*** Settings ***
Library         MyLibFile.py
Library         MyLibDir
Library         MyLibDir/
Library         dir_for_libs/MyLibFile2.py
Library         dir_for_libs/lib1/Lib.py  WITH NAME  lib1
Library         dir_for_libs/lib2/Lib.py  WITH NAME  lib2
Library         ${MYVAR}/MyLibDir2/
Library         MyJavaLib.java
Library         MyJavaLib2.class
Library         MyInvalidLibFile.py
Library         java_libraries.html
Library         library_scope/
Library         spaces in path/SpacePathLib.py
Library         this_does_not_exist.py

*** Variables ***
${MYVAR}  ${CURDIR}${/}dir_for_libs

*** Test Cases ***
Importing Python Library In File By Path
    Keyword In My Lib File
    ${ret} =  Keyword In My Lib File 2  world
    Should Be Equal  ${ret}  Hello world!

Importing Python Library In Dir By Path
    ${ret} =  MyLibDir.Keyword In My Lib Dir
    Should Be Equal  ${ret}  Executed keyword 'Keyword In My Lib Dir' with args [ ]
    ${ret} =  Keyword In My Lib Dir  a1  a2
    Should Be Equal  ${ret}  Executed keyword 'Keyword In My Lib Dir' with args [ a1 | a2 ]

Importing Library With Same Name
    lib1.Hello
    lib2.Hello
    Kw from lib1
    Kw from lib2

Importing Python Library By Path With Variables
    ${sum} =  Keyword In My Lib Dir 2  1  2  3  4  5
    Should Be Equal  ${sum}  ${15}

Importing Java Library File By Path With .java Extension
    ${ret} =  Keyword In My Java Lib  tellus
    Should Be Equal  ${ret}  Hi tellus!

Importing Java Library File By Path With .class Extension
    ${ret} =  MyJavaLib2. Keyword In My Java Lib 2  maailma
    Should Be Equal  ${ret}  Moi maailma!

Importing By Path Having Spaces
    ${ret} =  Spaces in Library Path
    Should Be Equal  ${ret}  here was a bug

