*** Settings ***
Suite Setup    Run Remote Tests    library_info.robot    libraryinfo.py
Resource       remote_resource.robot

*** Test Cases ***
Load large library
    Check Test Case    ${TESTNAME}
