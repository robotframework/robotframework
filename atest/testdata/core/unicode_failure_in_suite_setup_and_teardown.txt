*** Settings ***
Suite Setup     Raise Unicode Error
Suite Teardown  Raise Unicode Error
Library         UnicodeLibrary

*** Test Cases ***
Unicode Failure In Suite Setup and Teardown
    [Documentation]  FAIL  Parent suite setup failed:
    ...    Circle is 360°, Hyvää üötä, উৄ ৰ ৺ ট ৫ ৪ হ
    ...
    ...    Also parent suite teardown failed:
    ...    Circle is 360°, Hyvää üötä, উৄ ৰ ৺ ট ৫ ৪ হ

