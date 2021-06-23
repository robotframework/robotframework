*** Settings ***
Suite teardown    ${suite teardown}   World!

*** Test Cases ***
Setting teardowns with variables dynamically
    Set test variable    ${test teardown}   Log
    Set suite variable   ${suite teardown}   Log
    [teardown]   ${test teardown}    Hello
