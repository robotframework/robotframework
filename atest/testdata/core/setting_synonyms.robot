***Settings***
Test precondition    Log  Test Precondition from Setting table  	 	
Test Post Condition  Log  Test Postcondition from Setting table 		
Suite Pre Condition  Log  Suite Precondition 		
suitepostcondition   Log  Suite Postcondition
Documentation        NO RIDE

***Test Cases***
Pre and Post Condition from Setting Table
    No Operation

Pre and Post Condition for Test
    [Precondition]  Log  Precondition for test 	
    No Operation
    [ Post Condition ]  Log  Postcondition for test 	

Overriding Pre and Post conditions With Setup And teardown
    [Setup]  Log  Setup for test 	
    No Operation
    [Teardown]
