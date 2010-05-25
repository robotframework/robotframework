*** Settings ***	value
				
Test Setup			Set Log Level		   	DEBUG

* Test Cases *
Test With Tabs
	[ Documentation ]	FAIL 2 != 1
	Log				I ignore tabs		DEBUG			
	:FOR	${i}	IN	1	2
	\	Should Be Equal		${i}		1