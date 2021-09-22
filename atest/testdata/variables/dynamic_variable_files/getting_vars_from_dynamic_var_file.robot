*** Settings ***
Variables  dyn_vars.py  dict
Variables  dyn_vars.py  mydict
Variables  dyn_vars.py  Mapping
Variables  dyn_vars.py  UserDict
Variables  dyn_vars.py  MyUserDict

*** Test Cases ***
Variables From Dict Should Be Loaded
    Should Be Equal  ${from dict}  This From Dict
    Should Be Equal  ${from dict2}  ${2}

Variables From My Dict Should Be Loaded
    Should Be Equal  ${from my dict}  This From My Dict
    Should Be Equal  ${from my dict2}  ${2}

Variables From Mapping Should Be Loaded
    Should Be Equal  ${from Mapping}  This From Mapping
    Should Be Equal  ${from Mapping2}  ${2}

Variables From UserDict Should Be Loaded
    Should Be Equal  ${from userdict}  This From UserDict
    Should Be Equal  ${from userdict2}  ${2}

Variables From My UserDict Should Be Loaded
    Should Be Equal  ${from my userdict}  This From MyUserDict
    Should Be Equal  ${from my userdict2}  ${2}
