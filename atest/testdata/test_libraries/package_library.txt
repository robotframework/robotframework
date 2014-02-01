*** Settings ***
Library           MyLibDir
Library           MyLibDir.MyLibDir
Library           MyLibDir2
Library           MyLibDir.ClassLib
Library           MyLibDir.ClassLib.ClassLib
Library           MyLibDir.SubModuleLib
Library           MyLibDir.SubPackage
Library           MyLibDir.SubPackage.SubPackage
Library           MyLibDir.SubPackage2
Library           MyLibDir.SubPackage.ClassLib
Library           MyLibDir.SubPackage.ClassLib.ClassLib
Library           MyLibDir.SubPackage.SubModuleLib

*** Test Cases ***
Class in package as library implicitly
    MyLibDir.Keyword In My Lib Dir

Class in package as library explicitly
    MyLibDir.MyLibDir.Keyword In My Lib Dir

Package itself as library
    MyLibDir2.Keyword In My Lib Dir 2

Class in sub-module as library implicitly
    MyLibDir.ClassLib.Keyword In MyLibDir ClassLib

Class in sub-module as library explicitly
    MyLibDir.ClassLib.ClassLib.Keyword In MyLibDir ClassLib

Sub-module itself as library
    MyLibDir.SubModuleLib.Keyword In MyLibDir SubModuleLib

Class in sub-package as library implicitly
    MyLibDir.SubPackage.Keyword In MyLibDir SubPackage Class

Class in sub-package as library explicitly
    MyLibDir.SubPackage.SubPackage.Keyword In MyLibDir SubPackage Class

Sub-package itself as library
    MyLibDir.SubPackage2.Keyword In MyLibDir SubPackage2 Package

Class in sub-sub-module as library implicitly
    MyLibDir.SubPackage.ClassLib.Keyword In MyLibDir SubPackage ClassLib

Class in sub-sub-module as library explicitly
    MyLibDir.SubPackage.ClassLib.ClassLib.Keyword In MyLibDir SubPackage ClassLib

Sub-sub-module itself as library
    MyLibDir.SubPackage.SubModuleLib.Keyword In MyLibDir SubPackage SubModuleLib
