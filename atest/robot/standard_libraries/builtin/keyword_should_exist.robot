*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/keyword_should_exist.txt
Force Tags      regression  pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***

Library keyword exists with short name
    Check Test Case  ${TESTNAME}

Library keyword exists with full name
    Check Test Case  ${TESTNAME}

Local user keyword exists
    Check Test Case  ${TESTNAME}

User keyword in resource exists with short name
    Check Test Case  ${TESTNAME}

User keyword in resource exists with full name
    Check Test Case  ${TESTNAME}

Variables in keyword name
    Check Test Case  ${TESTNAME}

BDD style keyword exists
    Check Test Case  ${TESTNAME}

Keyword does not exist
    Check Test Case  ${TESTNAME}

Keyword does not exist with custom message
    Check Test Case  ${TESTNAME}

Duplicate keywords
    Check Test Case  ${TESTNAME}

Duplicate keywords in same resourc
    Check Test Case  ${TESTNAME}

Higher priority keyword overrides
    Check Test Case  ${TESTNAME}

Empty keyword name
    Check Test Case  ${TESTNAME}

Non-string keyword name
    Check Test Case  ${TESTNAME}

