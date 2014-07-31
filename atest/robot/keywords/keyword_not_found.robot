*** Settings ***
Documentation   Test cases for situations where non-existing keywords are used. Situations where keyword exist or the are too many keywords are tested in keyword_namespaces.html.
Suite Setup     Run Tests  ${EMPTY}  keywords/keyword_not_found.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***
Non Existing Implicit Keyword
    Check Test Case  Non Existing Implicit Keyword 1
    Check Test Case  Non Existing Implicit Keyword 2

Non Existing Explicit Keyword
    Check Test Case  Non Existing Explicit Keyword 1
    Check Test Case  Non Existing Explicit Keyword 2

Non Existing Impicit In User Keyword
    Check Test Case  Non Existing Impicit In User Keyword

Non Existing Explicit In User Keyword
    Check Test Case  Non Existing Explicit In User Keyword

Non Existing Library
    Check Test Case  Non Existing Library

