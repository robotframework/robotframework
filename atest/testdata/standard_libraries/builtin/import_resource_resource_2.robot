*** Settings ***
Library  Collections


*** Variables ***
${VAR FROM IMPORT RESOURCE RESOURCE 2}  value 2
${COMMON VAR}  resource 2


*** Keywords ***
KW From Import Resource Resource 2
    No Operation
