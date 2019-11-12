*** Settings ***    header  with      spaces
Test Setup			Set Log Level		   	DEBUG


*** Test Cases ***	header	  with			tabs
Minimum spaces  [Documentation]  FAIL The End
  No Operation
  Fail  The End

Inconsistent indentation
               [Documentation]    FAIL    The End
    No Operation
                                  Fail    The End

Lot of spaces                                [Documentation]                         FAIL                                  The End
                                                             No Operation
                    Fail                                                           The End

Trailing spaces
    [Documentation]    Don't let you editor eat these!!
    Log    No spaces at end 
    Log    One space at end 
    Log    Two spaces at end  
    Log    Ten spaces at end          
    Log    Tab at end	

Tabs
	[Documentation]		FAIL		2 != 1
	Log				I ignore tabs		DEBUG
	FOR	${i}	IN	1	2
		Should Be Equal		${i}		1
	END

Tabs and spaces
  	[Documentation]		  FAIL	  	2 != 1
	    Log	   		  	I ignore tabs (and spaces)	  	DEBUG
	FOR	${i}	IN	1	2
  		   Should Be Equal		${i}	  	1
	   END
