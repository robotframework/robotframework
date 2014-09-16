*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/parsing.robot
Force Tags       regression    pybot    jybot
Resource         xml_resource.robot

*** Test Cases ***
Parse file using forwards slash as path separator
    Check Test Case    ${TESTNAME}

Parse file using system path separator
    Check Test Case    ${TESTNAME}

Parse string
    Check Test Case    ${TESTNAME}

Parse invalid file
    Check Test Case    ${TESTNAME}

Parse invalid string
    Check Test Case    ${TESTNAME}

Parse non-existing file
    Check Test Case    ${TESTNAME}
