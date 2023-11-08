*** Settings ***
Library           ImportRobotModuleTestLibrary.py
Library           OperatingSystem

*** Test Cases ***
Internal modules cannot be imported directly
    Importing Robot Module Directly Fails

Internal modules can be imported through `robot.`
    Importing Robot Module Through Robot Succeeds

Standard libraries cannot be imported directly
    Importing Standard Library Directly Fails

Standard libraries can be imported through `robot.libraries.`
    Importing Standard Library Through Robot Libraries Succeeds
    Should Be Equal    ${SET BY LIBRARY}    ${42}

In test data standard libraries can be imported directly
    Directory Should Exist    .
    OperatingSystem.Directory Should Exist    .
