*** Settings ***
Documentation       Suite without custom name

Suite Name          Child without parent init


*** Test Cases ***
Test Case 01
    No Operation
# Verify That Suite Name is not a file like name
#     Should Not Contain    ${SUITE_NAME}    Parent Init Suite.Child Tests02.Child0202

# Verify Suite Name
#     Should Contain    ${SUITE_NAME}    Parent Init Suite.Child Tests02.Child without parent init
