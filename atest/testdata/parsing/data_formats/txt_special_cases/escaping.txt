*Settings*
Variables  ../../escaping_variables.py

*Test Cases *
|  Escaping Pipe  |  Should Be Pipe  |  \|  |

| Using " In Data | Should Not Be Equal | "foo" | foo | 
                    Should Not Be Equal   "foo"   foo   

*Keywords*
|  Should Be Pipe  |  [Arguments]      |  ${arg}  |
|                  |  Should Be Equal  |  ${arg}  |  ${pipe}  |  