*** Settings ***
Library         OperatingSystem
Library         E x a m p l e L i b r a r y
Library         libmodule.LibClass1
Library         lib module . Lib Class 2
Library         libmodule
Library         NamespaceUsingLibrary

*** Test Cases ***
Normal Library Import
    Directory Should Not Be Empty  ${CURDIR}
    Directory Should Exist  %{TEMPDIR}

Library Import With Spaces In Name
    Print  It works!
    example Library. print many  It really  workz!!

Importing Python Class From Module
    ${ret1} =  Verify Lib Class 1
    ${ret2} =  libmodule . LibClass2 . Verify Lib Class 2
    Should Be Equal  ${ret1}  LibClass 1 works
    Should Be Equal  ${ret2}  LibClass 2 works also

Namespace is initialized during library init
    ${importing suite}=   Get Importing Suite
    Should Be Equal   ${importing suite}   ${SUITE NAME}
    ${lib}=   Get Other Library
    Should Be Equal   ${lib.__name__}    robot.libraries.Easter
