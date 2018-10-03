*** Settings ***
Suite Setup       Raise Non ASCII Error
Suite Teardown    Raise Non ASCII Error
Library           NonAsciiLibrary

*** Test Cases ***
Non-ASCII Failure In Suite Setup and Teardown
    [Documentation]  FAIL  Parent suite setup failed:
    ...    Circle is 360°, Hyvää üötä, উৄ ৰ ৺ ট ৫ ৪ হ
    ...
    ...    Also parent suite teardown failed:
    ...    Circle is 360°, Hyvää üötä, উৄ ৰ ৺ ট ৫ ৪ হ
