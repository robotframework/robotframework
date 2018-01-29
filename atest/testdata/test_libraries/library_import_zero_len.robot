*** Settings ***

Library        LenLibrary

*** Test Cases ***

Verify Zero Length Library Import
   ${lenlib}=    Get Library Instance     LenLibrary
   Should be Empty   ${lenlib}
   LenLibrary.Set Length    1
   ${len}=    Get Length    ${lenlib}
   Should Be Equal As Integers    ${len}    1
