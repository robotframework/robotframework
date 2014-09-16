*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/save_xml.robot
Force Tags       regression    pybot    jybot
Resource         xml_resource.robot

*** Test Cases ***

Save XML Element
    Check Test Case    ${TESTNAME}

Save XML String
    Check Test Case    ${TESTNAME}

Save XML File
    Check Test Case    ${TESTNAME}

Save XML Using Custom Encoding
    Check Test Case    ${TESTNAME}

Save Non-ASCII XML
    Check Test Case    ${TESTNAME}

Save Non-ASCII XML Using Custom Encoding
    Check Test Case    ${TESTNAME}

Save to Invalid File
    Check Test Case    ${TESTNAME}

Save Using Invalid Encoding
    Check Test Case    ${TESTNAME}

Save Non-ASCII Using ASCII
    Check Test Case    ${TESTNAME}
