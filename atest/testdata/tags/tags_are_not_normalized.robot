*** Settings ***
Force Tags    
Default Tags  

*** Test Cases ***
Case Is Not Altered
    [Tags]  lower  UPPER  MiXeD
    No Operation

Spaces Are Not Removed
    [Tags]  One space  2 \ spaces  Seven${SPACE*7}spaces
    No Operation

Undersscores and similar are not removed
    [Tags]  _under_scores_  hyp-HEN and d.o.t.s.  !"#%&/()=
    No Operation

Sorting Is Normalized
    [Tags]  a1  A2  A 0
    No Operation

Normalized Duplicates Are Removed
    [Tags]  hello  HeLLo  HELLO  ${EMPTY}  H e l l o
    No Operation

Tags To Stats
    [Tags]  tag

Tags To Stats
    [Tags]  tAg

Tags To Stats
    [Tags]  TAG

Tags To Stats
    [Tags]  ta g

Tags To Stats
    [Tags]  T A G

Excluded
    [Tags]  exclude

Excluded
    [Tags]  e x c l u d e

Excluded
    [Tags]  EXCLUDE

Excluded
    [Tags]  exclude2

Excluded
    [Tags]  Ex C Lude 2

