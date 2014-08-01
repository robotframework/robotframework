*** Settings ***

*** Test Cases ***
Non Existing Implicit Keyword 1
    [Documentation]  FAIL No keyword with name 'No Keyword With This Name' found.
    No Keyword With This Name

Non Existing Implicit Keyword 2
    [Documentation]  FAIL No keyword with name 'this name is NOT altered' found.
    this name is NOT altered

Non Existing Explicit Keyword 1
    [Documentation]  FAIL No keyword with name 'BuiltIn.No Keyword With This Name' found.
    BuiltIn.No Operation
    BuiltIn.No Keyword With This Name

Non Existing Explicit Keyword 2
    [Documentation]  FAIL No keyword with name 'built in. ThisName is _not_ altered' found.
    built in . n o o PERA ti on
    built in. ThisName is _not_ altered

Non Existing Impicit In User Keyword
    [Documentation]  FAIL No keyword with name 'No Keyword With This Name' found.
    Non Existing Implicit In User Keyoword

Non Existing Explicit In User Keyword
    [Documentation]  FAIL No keyword with name 'BuiltIn.No Keyword With This Name' found.
    Non Existing Explicit In User Keyword

Non Existing Library
    [Documentation]  FAIL No keyword with name 'NoSuchLib.NOOP' found.
    NOOP
    NoSuchLib.NOOP

*** Keywords ***
Non Existing Implicit In User Keyoword
    No Keyword With This Name

Non Existing Explicit In User Keyword
    BuiltIn.No Keyword With This Name

