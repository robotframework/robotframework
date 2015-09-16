*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/add_and_remove_elements_with_lxml.robot
Force Tags       require-lxml
Resource         xml_resource.robot

*** Test Cases ***
Add Element
    Check Test Case    ${TESTNAME}

Add Element As String
    Check Test Case    ${TESTNAME}

Add Element With Index
    Check Test Case    ${TESTNAME}

Added Element Is A Copy
    Check Test Case    ${TESTNAME}

Add Element Returns Root Element
    Check Test Case    ${TESTNAME}

Remove Element
    Check Test Case    ${TESTNAME}

Remove Non-Direct Child Element
    Check Test Case    ${TESTNAME}

Remove Element Keeps Tail By Default
    Check Test Case    ${TESTNAME}

Remove Element Keeps Tail When Parent or Sibling Contains No Text
    Check Test Case    ${TESTNAME}

Remove Element Can Be Configured To Remove Tail
    Check Test Case    ${TESTNAME}

Remove Element Fails If No Element Match
    Check Test Case    ${TESTNAME}

Remove Element Fails If Multiple Elements Match
    Check Test Case    ${TESTNAME}

Remove Element Requires Xpath
    Check Test Case    ${TESTNAME}

Remove Element Cannot Remove Root Element
    Check Test Case    ${TESTNAME}

Remove Element Returns Root Element
    Check Test Case    ${TESTNAME}

Remove Elements
    Check Test Case    ${TESTNAME}

Remove Elements Can Remove All Child Elements
    Check Test Case    ${TESTNAME}

Remove Elements Does Not Fail If No Element Match
    Check Test Case    ${TESTNAME}

Remove Elements Keeps Tail By Default
    Check Test Case    ${TESTNAME}

Remove Elements Can Be Configured To Remove Tail
    Check Test Case    ${TESTNAME}

Remove Elements Requires Xpath
    Check Test Case    ${TESTNAME}

Remove Elements Cannot Remove Root Element
    Check Test Case    ${TESTNAME}

Remove Elements Returns Root Element
    Check Test Case    ${TESTNAME}
