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
Library         OperatingSystem    # This succeeds after all failed imports

*** Variables ***
${CLASH WITH BUILTIN}    %{TEMPDIR}${/}sys.py

*** Test Cases ***
Name clash with Python builtin-module
    [Documentation]    FAIL
    ...    Importing library '${CLASH WITH BUILTIN}' failed: \
    ...    Cannot import custom module with same name as Python built-in module.
    Create File    ${CLASH WITH BUILTIN}    def kw(): pass
    Import library    ${CLASH WITH BUILTIN}
    [Teardown]    Remove File    ${CLASH WITH BUILTIN}
