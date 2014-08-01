*** Settings ***
Suite Setup     Run Tests  \  core/import_settings.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***

Library Import
    Check testcase  Library Import

Resource Import
    Check testcase  Resource Import

Variable Import
    Check testcase  Variable Import

