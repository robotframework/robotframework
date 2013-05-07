*** Settings ***
Library         MyInvalidLibFile.py
Library         InitializationFailLibrary.py
Library         InitializationFailLibrary.py    ${1}    arg2=${2}
Library         InitializationFailLibrary.py    too    many    values
Library         InitializationFailJavaLibrary.java

*** Test Cases ***
Test
    Comment  Tests only failing library imports.

