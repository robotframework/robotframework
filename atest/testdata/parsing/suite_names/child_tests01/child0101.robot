*** Settings ***
Documentation       Just a sample suite with a name took from the filename


*** Test Cases ***
Test Case 1
    No Operation
# Verify That Suite Name is not a file like name
#     Should Not Contain    ${SUITE_NAME}    Parent Init Suite.Child Tests01.Child0101

# Verify Suite Name
#     Should Contain    ${SUITE_NAME}    Parent Init Suite.Child Suite01 Name.Child0101