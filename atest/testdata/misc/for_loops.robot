*** Settings ***
Documentation    Initially created for testing for loops with testdoc but
...              can be used also for other purposes and extended as needed.

*** Test Cases ***
For Loop In Test
    :: FOR    ${pet}    IN    cat    dog    horse
    \    Log    ${pet}

For In Range Loop In Test
    :: FOR    ${i}    IN RANGE    10
    \    Log    ${i}
