| *** Settings *** |
| Library | OperatingSystem |
|
| Library | String
|
||
|Documentation    invalid

| *** Comments ***
|
||
|||
||||
|| |
| ||

***Test Cases***
| Minimum Pipes
| | No Operation

|  Pipes All Around  |  No Operation  |
|                    |  Log  |  New Line  |

|
|
| Empty line with pipe
|
| | Directory Should Exist | . |
|
|
|
| | Convert To Upper Case | Using keywords from imported libraries
|
|

| Pipes In Data |
|               | Should Be Equal | |foo\| | |foo| |
|               | Should Be Equal | |foo|  | |foo\|
|               | Should Be Equal | \|     | ${{'|'}} |
|               | Should Be Equal | ||||   | ${{'||||'}}  |


|  Extra Pipes At The End  |       |                      |       |        |
|                          |  Log  | Also spaces after the last pipe. Don't let your IDE eat them!
|                          |  Log  |  Line Ends to \|  |    |       |
|                          |  Log  |  Line Ends to \| + 1 space   |       |        | 
|                          |  Log  |  Line Ends to \| + 2 space   |       |        |  
|                          |  Log  |  Line Ends to \| + 3 space   |       |        |   
|                          |  Log  |  Line Ends to \| + 4 space   |       |        |    
|                          |  Log  |  Line Ends to \| + 10 space   |       |        |          
|                          |  Log  |  Line Ends to \| + 100 space   |       |        |                                                                                                    
| Empty Cells In Middle |
|                       |                        |
| | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
|
| |
|  |
|   |
|    |
|     |
|      |
|       |
|      |
|     |
|    |
|   |
|  |
| |
|
| |  |   |    |     |      |       |        |       |      |     |    |  | |
| | Cells Should Be Empty  |  |     | | | |  |   | ${EMPTY}  | | | |

| Consecutive spaces
| | Should Be Equal | foo            bar | foo${SPACE * 12}bar
| | Should Be Equal | non-ascii  　spaces | non-ascii\xa0\u1680\u3000spaces

| Tabs
| | Should Be Equal | foo	bar | foo\tbar |
| | Should Be Equal | foo			bar | foo\t\t\tbar |

| Using FOR Loop With Pipes  |
|         |  [Documentation]  |  FAIL    |  for loop executed  |
|         |   FOR  |  ${value}  |  IN   |  a    |   a   |   for loop executed   |  for loop not executed  |
|         |        |  Should Be Equal  |  ${value}  |  a   |  ${value}  |  no values  |
|         | END    |

|Leading pipe without space after
    |Leading pipe without space after

||  ||

| *Keywords* | A | r | g | u | m | e | n | t | s |
|  Cells Should Be Empty  |
|       | [Arguments]     | @{args}          |
|       |  FOR            | ${arg}           |  IN      |  @{args}   |
|       |                 | Should Be Equal  |  ${arg}  |  ${EMPTY}  |
|       | END             |
|       | ${length} =     | Get Length       | ${args}  |
|       | Should Be Equal | ${length}        | ${8}     | Amount of empty cells |

|Leading pipe without space after
    No Operation

||  |||  ||||

|||   [Arguments]    ${arg}
      Should Be Equal    ${arg}    ||||
