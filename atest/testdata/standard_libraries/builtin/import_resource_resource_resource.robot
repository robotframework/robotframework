*** Settings ***
Resource  import_resource_resource_resource.robot
Variables  import_resource_vars.py  VAR FROM VARFILE X  ${VARFILE VALUE}
Library  ${LIBRARY}

*** Variables ***
${VAR FROM IMPORT RESOURCE RESOURCE RESOURCE}  value x
${LIBRARY}  OperatingSystem
${VARFILE VALUE}  Default varfile value

*** Keywords ***
KW From Import Resource Resource Resource
    No Operation
