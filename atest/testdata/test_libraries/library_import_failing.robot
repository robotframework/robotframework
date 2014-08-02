*** Settings ***
Library         MyInvalidLibFile.py
Library         InitializationFailLibrary.py
Library         InitializationFailLibrary.py    ${1}    arg2=${2}
Library         InitializationFailLibrary.py    too    many    values
Library         InitializationFailLibrary.py    arg2=invalid    usage
Library         NonExistingLibrary
Library         ${non existing nön äscii}
Library         InitializationFailLibrary.py    ${nön existing}    ${vars here}
Library         # Missing name causes error
Library         InitializationFailJavaLibrary.java

*** Test Cases ***
Dummy test
    Comment    Only testing imports here
