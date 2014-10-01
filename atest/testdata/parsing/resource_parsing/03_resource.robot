*** Setting ***
Resource          02_resource.robot

*** Variable ***
${var_from_03_resource}    variable value from 03 resource

*** Keyword ***
Keyword From 03 Resource
    Log    ${var_from_03_resource}
    Log    ${var_from_02_resource}
    Keyword From 02 Resource
