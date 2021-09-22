*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/save_xml.robot
Resource         xml_resource.robot

*** Test Cases ***
Save XML Element
    ${tc} =    Check Test Case    ${TESTNAME}
    ${path} =    Normalize Path    %{TEMPDIR}/xmllib.xml
    Check Log Message    ${tc.kws[1].msgs[0]}
    ...    XML saved to <a href="file://${path}">${path}</a>.    html=True

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

Doctype is not preserved
    Check Test Case    ${TESTNAME}

Comments and processing instructions are removed
    Check Test Case    ${TESTNAME}

Element can be further modified after saving
    Check Test Case    ${TESTNAME}

Element with namespaces can be further modified after saving
    Check Test Case    ${TESTNAME}
