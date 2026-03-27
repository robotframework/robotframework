*** Settings ***
Resource     resources_and_variables/resources.robot    WITH NAME    MyAlias

*** Test Cases ***
Resource Import With Alias
    [Documentation]  Test that resource file can be imported with an alias.
    Should Be Equal  ${resources}  Variable from resources.robot
    MyAlias.Resources
