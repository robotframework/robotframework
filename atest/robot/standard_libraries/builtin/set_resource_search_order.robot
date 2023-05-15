*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/set_resource_search_order
Resource        atest_resource.robot

*** Test Cases ***
Resource Order Set In Suite Setup Should Be Available In Test Cases
    Check Test Case  ${TEST NAME}

Empty Resource Order Can Be Set
    Check Test Case  ${TEST NAME}

One Resource Can Be Set As Default Resource
    Check Test Case  ${TEST NAME}

More Than One Resources Can Be Set As Default Resources
    Check Test Case  ${TEST NAME}

Non-Existing Resources In Search Order Are Ignored
    Check Test Case  ${TEST NAME}

Resource Order Should Be Available In The Next Test Case
    Check Test Case  ${TEST NAME}

Setting Resource Order Returns Previous Resource Order
    Check Test Case  ${TEST NAME}

It Is Possible To Set Both Library And Resource Priorities At The Same Time
    Check Test Case  ${TEST NAME}

Resources Always Have Higher Priority Than Libraries
    Check Test Case  ${TEST NAME}

Resource Search Order Is Space Insensitive
    Check Test Case  ${TEST NAME}

Resource Search Order Is Case Insensitive
    Check Test Case  ${TEST NAME}

Default Resource Order Should Be Suite Specific
    Check Test Case  ${TEST NAME}

Search Order Controlled Match Containing Embedded Arguments Wins Over Exact Match
    Check Test Case  ${TEST NAME}

Best Search Order Controlled Match Wins In Resource
    Check Test Case  ${TEST NAME}
