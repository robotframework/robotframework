*** Settings ***
Documentation     Init file doc.
Suite setup       Set suite documentation    ${SUITE DOCUMENTATION} Concatenated in setup.
Suite teardown    Should be equal    ${SUITE DOCUMENTATION}    Init file doc. Concatenated in setup. Appended in test.
