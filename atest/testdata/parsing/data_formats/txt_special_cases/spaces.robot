*Test Cases*
Minimum Spaces  No Operation

Spaces All Around  No Operation  
                                   
                  Log           New Line  

Extra Spaces At The End                             
                         Log  Line Ends to empty
                         Log  Line Ends to 1 space
                         Log  Line Ends to 2 space  
                         Log  Line Ends to 3 space   
                         Log  Line Ends to 4 space    
                         Log  Line Ends to 10 space          
                         Log  Line Ends to 100 space                                                                                                    

Using FOR Loop With Spaces
         [Documentation]  FAIL  for loop executed

	 ${error} =  Set Variable  \

	 : FOR  ${word}  IN  for  loop  executed

         \  ${error} =  Catenate  
         ...  ${error}  ${word}

         :FOR  ${value}  IN  aaa     AAA  aAa    
         ...       AaA         AAa       aAA    ${error.strip()}

         \     Should Be Equal   ${value.lower()}   aaa    ${value}   
         \  ...  no values  
