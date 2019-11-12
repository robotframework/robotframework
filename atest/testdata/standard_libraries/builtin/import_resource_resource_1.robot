*** Settings ***
Variables  import_resource_vars.py  VAR FROM VARFILE 1  VALUE FROM VARFILE 1
Resource  import_resource_resource_resource.robot


*** Variables ***
${VAR FROM IMPORT RESOURCE RESOURCE}  value 1
${COMMON VAR}  resource 1


*** Keywords ***
KW From Import Resource Resource
    No Operation
