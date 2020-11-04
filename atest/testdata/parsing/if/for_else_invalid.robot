*** Test Cases ***
For else if invalid
    FOR  ${value}  IN  1  2  3
       IF  ${value} == 1
           Log  ${value}
       ELSE
           No Operation
       ELSE IF  ${value} == 3
           Log  something
       END
   END