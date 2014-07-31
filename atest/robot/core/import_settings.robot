*** Settings ***
Suite Setup     Run Tests  \  core/import_settings.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***

Library Import
    Check testcase  Library Import

Resource Import
    Check testcase  Resource Import

Variable Import
    Check testcase  Variable Import

