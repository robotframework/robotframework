*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/set_library_search_order
Resource        atest_resource.robot

*** Test Cases ***
Library Order Set In Suite Setup Should Be Available In Test Cases
    Check Test Case  ${TEST NAME}

Empty Library Order Can Be Set
    Check Test Case  ${TEST NAME}

One Library Can Be Set As Default Library
    Check Test Case  ${TEST NAME}

More Than One Library Can Be Set As Default Libraries
    Check Test Case  ${TEST NAME}

Non-Existing Libraries In Search Order Are Ignored
    Check Test Case  ${TEST NAME}

Library Order Should Be Available In The Next Test Case
    Check Test Case  ${TEST NAME}

Setting Library Order Returns Previous Library Order
    Check Test Case  ${TEST NAME}

Setting Library Order Allows Setting BuiltIn Library As Default Library
    Check Test Case  ${TEST NAME}

Setting Library Order Allows Setting Own Library Before BuiltIn Library
    Check Test Case  ${TEST NAME}

Default Library Order Should Be Suite Specific
    Check Test Case  ${TEST NAME}

Library Search Order Is Space Insensitive
    Check Test Case  ${TEST NAME}

Library Search Order Is Case Insensitive
    Check Test Case  ${TEST NAME}

Search Order Controlled Match Containing Embedded Arguments Wins Over Exact Match
    Check Test Case  ${TEST NAME}
    
Best Search Order Controlled Match Wins In Library
    Check Test Case  ${TEST NAME}
