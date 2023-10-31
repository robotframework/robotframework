*** Settings ***
Library         Operating System

*** Variables ***
@{LIST}  a  b  c
@{EMPTY LIST}
@{1 ITEM}  1
@{2 ITEMS}  @{1 ITEM}  2
@{3 ITEMS}  @{2 ITEMS}  3
@{3 ITEMS 2}  0  @{2 ITEMS}
@{4 ITEMS}  @{3 ITEMS}  4
@{4 ITEMS 2}  0  @{3 ITEMS}
@{5 ITEMS}  @{4 ITEMS}  5
@{NEEDS ESCAPING}  c:\\temp\\foo  \${notvar}
@{NEEDS ESCAPING 2}  len("\\\\") == 1  @{NEEDS ESCAPING}
@{NEEDS ESCAPING 3}  @{3 ITEMS 2}  @{NEEDS ESCAPING}

*** Test Cases ***
True Condition
    ${var} =  Set Variable If  1 > 0  this is set  this is not
    Should Be Equal  ${var}  this is set
    ${var} =  Set Variable If  True  only one value
    Should Be Equal  ${var}  only one value
    ${var} =  Set Variable If  ${True}  ${LIST[1]}  whatever
    Should Be Equal  ${var}  b
    @{var} =  Set Variable If  "this is also a true value"  ${LIST[:-1]}  whatever
    Should Be True  @{var} == ['a','b']

False Condition
    ${var} =  Set Variable If  0 > 1  this value is not used  ${LIST}
    Should Be True  ${var} == ['a','b','c']
    ${var} =  Set Variable If  ${False}  still not used
    Should Be Equal  ${var}  ${None}

Invalid Expression
    [Documentation]  FAIL STARTS: Evaluating expression 'invalid expr' failed: SyntaxError:
    Set Variable If  invalid expr  whatever  values

Fails Without Values 1
    [Documentation]  FAIL At least one value is required.
    Set Variable If  True

Fails Without Values 2
    [Documentation]  FAIL At least one value is required.
    Set Variable If  False

Non-Existing Variables In Values 1
    [Documentation]  FAIL Variable '\${now this breaks}' not found.
    ${existing} =  Set Variable  ${42}
    ${var} =  Set Variable If  True  ${existing}*2 = ${existing*2}  ${nonex}
    Should Be Equal  ${var}  42*2 = 84
    ${var} =  Set Variable If  ${existing} < 0  ${I don't exist at all!!}
    Should Be Equal  ${var}  ${None}
    ${var} =  Set Variable If  ${existing}  ${now this breaks}  Not used

Non-Existing Variables In Values 2
    [Documentation]  FAIL Resolving variable '${nonexisting.extended}' failed: Variable '${nonexisting}' not found.
    ${var} =  Set Variable If  False is True  ${not used}  ${nonexisting.extended}

Non-Existing Variables In Values 3
    [Documentation]  FAIL Variable '\${ooooops}' not found.
    Set Variable If  False  ${not used}  True  ${ooooops}

Non-Existing Variables In Values 4
    [Documentation]  FAIL STARTS: Resolving variable '\${SPACE.nonex}' failed: AttributeError:
    Set Variable If  False  ${not used}  False  ${not used}  ${SPACE.nonex}

Non-Existing Variables In Values 5
    [Documentation]  FAIL Variable '\${nonexisting}' not found.
    Set Variable If  False  ${not used}  False  ${not used}  True  This is ${nonexisting} is enough

Extra Values Are Ignored If First Expression Is True
    ${var} =  Set Variable If  True  This ${1} is set!!  Other  values  are  ${not}
    ...  used
    Should Be Equal  ${var}  This 1 is set!!

If / Else If
    ${var} =  Set Variable If  False  ${nonex} but not used  True  2nd expression is True so this value is set  ${nonex} but not used
    Should Be Equal  ${var}  2nd expression is True so this value is set
    ${var} =  Set Variable If  ${1} == 0  ${whatever}  ${1} < 0  ${whatever}  ${1} > 2  ${whatever}
    ...  ${1} == 1  Here we go!
    Should Be Equal  ${var}  Here we go!

If / Else If / Else
    ${var} =  Set Variable If
    ...  ${False}  this value is not used
    ...  ${None}   this value is not used
    ...  ${0}      this value is not used
    ...  Final else!
    Should Be Equal  ${var}  Final else!
    ${var} =  Set Variable If
    ...  ${False}  this value is not used
    ...  ${None}   this value is not used
    ...  ${0}      this value is not used
    Should Be Equal  ${var}  ${None}

With Empty List Variables 1
    [Documentation]  FAIL At least one value is required.
    Set Variable If  True  @{EMPTY LIST}

With Empty List Variables 2
    [Documentation]  FAIL At least one value is required.
    Set Variable If  False  @{EMPTY LIST}  @{EMPTY LIST}  @{EMPTY LIST}

With Empty List Variables 3
    ${v1} =  Set Variable If  True  42  @{EMPTY LIST}
    ${v2} =  Set Variable If  True  @{EMPTY LIST}  42
    ${v3} =  Set Variable If  @{EMPTY LIST}  True  42
    ${v4} =  Set Variable If  @{EMPTY LIST}  ${True}  ${42}
    ${v5} =  Set Variable If  @{EMPTY LIST}  @{EMPTY LIST}  ${True}  @{EMPTY LIST}  @{EMPTY LIST}  ${42}  @{EMPTY LIST}
    Should Be True  ${v1} == ${v2} == ${v3} == ${v4} == ${v5} == 42

With List Variables In Values
    ${var} =  Set Variable If  True  @{1 ITEM}
    Should Be Equal  ${var}  1
    ${var} =  Set Variable If  ${False}  @{1 ITEM}
    Should Be Equal  ${var}  ${None}
    ${var} =  Set Variable If  True  @{2 ITEMS}  @{EMPTY LIST}
    Should Be Equal  ${var}  1
    ${var} =  Set Variable If  False  @{EMPTY LIST}  @{2 ITEMS}
    Should Be Equal  ${var}  2
    ${var} =  Set Variable If  True  @{2 ITEMS} as string
    Should Be Equal  ${var}  @{2 ITEMS} as string

With List Variables In Expressions And Values
    ${var} =  Set Variable If  @{1 ITEM}  this is set
    Should Be Equal  ${var}  this is set
    ${var} =  Set Variable If  @{2 ITEMS}
    Should Be Equal  ${var}  2
    ${var} =  Set Variable If  @{2 ITEMS} == @{1 ITEM}  @{2 ITEMS}  value
    Should Be Equal  ${var}  value
    ${var} =  Set Variable If  @{3 ITEMS}
    Should Be Equal  ${var}  2
    ${var} =  Set Variable If  @{3 ITEMS 2}
    Should Be Equal  ${var}  2
    ${var} =  Set Variable If  @{4 ITEMS 2}
    Should Be Equal  ${var}  3

With List Variables Containing Escaped Values
    ${var} =  Set Variable If  True  @{NEEDS ESCAPING}
    Should Be Equal  ${var}  c:\\temp\\foo
    ${var} =  Set Variable If  False  @{NEEDS ESCAPING}
    Should Be Equal  ${var}  \${notvar}
    ${var} =  Set Variable If  @{NEEDS ESCAPING 2}
    Should Be Equal  ${var}  c:\\temp\\foo
    ${var} =  Set Variable If  @{NEEDS ESCAPING 3}
    Should Be Equal  ${var}  c:\\temp\\foo

Lot of conditions
    ${var} =    Set Variable If
    ...    ${0} > 0    not set
    ...    ${0} > 1    not set
    ...    ${0} > 2    not set
    ...    ${0} > 3    not set
    ...    ${0} > 4    not set
    ...    ${0} > 5    not set
    ...    ${0} > 6    not set
    ...    ${0} > 7    not set
    ...    ${0} > 8    not set
    ...    ${0} > 9    not set
    ...    ${0} > 10    not set
    ...    ${0} > 11    not set
    ...    ${0} > 12    not set
    ...    ${0} > 13    not set
    ...    ${0} > 14    not set
    ...    ${0} > 15    not set
    ...    ${0} > 16    not set
    ...    ${0} > 17    not set
    ...    ${0} > 18    not set
    ...    ${0} > 19    not set
    ...    ${0} > 20    not set
    ...    ${0} > 21    not set
    ...    ${0} > 22    not set
    ...    ${0} > 23    not set
    ...    ${0} > 24    not set
    ...    ${0} > 25    not set
    ...    ${0} > 26    not set
    ...    ${0} > 27    not set
    ...    ${0} > 28    not set
    ...    ${0} > 29    not set
    ...    ${0} > 30    not set
    ...    ${0} > 31    not set
    ...    ${0} > 32    not set
    ...    ${0} > 33    not set
    ...    ${0} > 34    not set
    ...    ${0} > 35    not set
    ...    ${0} > 36    not set
    ...    ${0} > 37    not set
    ...    ${0} > 38    not set
    ...    ${0} > 39    not set
    ...    ${0} > 40    not set
    ...    ${0} > 41    not set
    ...    ${0} > 42    not set
    ...    ${0} > 43    not set
    ...    ${0} > 44    not set
    ...    ${0} > 45    not set
    ...    ${0} > 46    not set
    ...    ${0} > 47    not set
    ...    ${0} > 48    not set
    ...    ${0} > 49    not set
    ...    ${0} > 50    not set
    ...    ${0} > 51    not set
    ...    ${0} > 52    not set
    ...    ${0} > 53    not set
    ...    ${0} > 54    not set
    ...    ${0} > 55    not set
    ...    ${0} > 56    not set
    ...    ${0} > 57    not set
    ...    ${0} > 58    not set
    ...    ${0} > 59    not set
    ...    ${0} > 60    not set
    ...    ${0} > 61    not set
    ...    ${0} > 62    not set
    ...    ${0} > 63    not set
    ...    ${0} > 64    not set
    ...    ${0} > 65    not set
    ...    ${0} > 66    not set
    ...    ${0} > 67    not set
    ...    ${0} > 68    not set
    ...    ${0} > 69    not set
    ...    ${0} > 70    not set
    ...    ${0} > 71    not set
    ...    ${0} > 72    not set
    ...    ${0} > 73    not set
    ...    ${0} > 74    not set
    ...    ${0} > 75    not set
    ...    ${0} > 76    not set
    ...    ${0} > 77    not set
    ...    ${0} > 78    not set
    ...    ${0} > 79    not set
    ...    ${0} > 80    not set
    ...    ${0} > 81    not set
    ...    ${0} > 82    not set
    ...    ${0} > 83    not set
    ...    ${0} > 84    not set
    ...    ${0} > 85    not set
    ...    ${0} > 86    not set
    ...    ${0} > 87    not set
    ...    ${0} > 88    not set
    ...    ${0} > 89    not set
    ...    ${0} > 90    not set
    ...    ${0} > 91    not set
    ...    ${0} > 92    not set
    ...    ${0} > 93    not set
    ...    ${0} > 94    not set
    ...    ${0} > 95    not set
    ...    ${0} > 96    not set
    ...    ${0} > 97    not set
    ...    ${0} > 98    not set
    ...    ${0} > 99    not set
    ...    ${0} > 100    not set
    ...    ${0} > 101    not set
    ...    ${0} > 102    not set
    ...    ${0} > 103    not set
    ...    ${0} > 104    not set
    ...    ${0} > 105    not set
    ...    ${0} > 106    not set
    ...    ${0} > 107    not set
    ...    ${0} > 108    not set
    ...    ${0} > 109    not set
    ...    ${0} > 110    not set
    ...    ${0} > 111    not set
    ...    ${0} > 112    not set
    ...    ${0} > 113    not set
    ...    ${0} > 114    not set
    ...    ${0} > 115    not set
    ...    ${0} > 116    not set
    ...    ${0} > 117    not set
    ...    ${0} > 118    not set
    ...    ${0} > 119    not set
    ...    ${0} > 120    not set
    ...    ${0} > 121    not set
    ...    ${0} > 122    not set
    ...    ${0} > 123    not set
    ...    ${0} > 124    not set
    ...    ${0} > 125    not set
    ...    ${0} > 126    not set
    ...    ${0} > 127    not set
    ...    ${0} > 128    not set
    ...    ${0} > 129    not set
    ...    ${0} > 130    not set
    ...    ${0} > 131    not set
    ...    ${0} > 132    not set
    ...    ${0} > 133    not set
    ...    ${0} > 134    not set
    ...    ${0} > 135    not set
    ...    ${0} > 136    not set
    ...    ${0} > 137    not set
    ...    ${0} > 138    not set
    ...    ${0} > 139    not set
    ...    ${0} > 140    not set
    ...    ${0} > 141    not set
    ...    ${0} > 142    not set
    ...    ${0} > 143    not set
    ...    ${0} > 144    not set
    ...    ${0} > 145    not set
    ...    ${0} > 146    not set
    ...    ${0} > 147    not set
    ...    ${0} > 148    not set
    ...    ${0} > 149    not set
    ...    ${0} > 150    not set
    ...    ${0} > 151    not set
    ...    ${0} > 152    not set
    ...    ${0} > 153    not set
    ...    ${0} > 154    not set
    ...    ${0} > 155    not set
    ...    ${0} > 156    not set
    ...    ${0} > 157    not set
    ...    ${0} > 158    not set
    ...    ${0} > 159    not set
    ...    ${0} > 160    not set
    ...    ${0} > 161    not set
    ...    ${0} > 162    not set
    ...    ${0} > 163    not set
    ...    ${0} > 164    not set
    ...    ${0} > 165    not set
    ...    ${0} > 166    not set
    ...    ${0} > 167    not set
    ...    ${0} > 168    not set
    ...    ${0} > 169    not set
    ...    ${0} > 170    not set
    ...    ${0} > 171    not set
    ...    ${0} > 172    not set
    ...    ${0} > 173    not set
    ...    ${0} > 174    not set
    ...    ${0} > 175    not set
    ...    ${0} > 176    not set
    ...    ${0} > 177    not set
    ...    ${0} > 178    not set
    ...    ${0} > 179    not set
    ...    ${0} > 180    not set
    ...    ${0} > 181    not set
    ...    ${0} > 182    not set
    ...    ${0} > 183    not set
    ...    ${0} > 184    not set
    ...    ${0} > 185    not set
    ...    ${0} > 186    not set
    ...    ${0} > 187    not set
    ...    ${0} > 188    not set
    ...    ${0} > 189    not set
    ...    ${0} > 190    not set
    ...    ${0} > 191    not set
    ...    ${0} > 192    not set
    ...    ${0} > 193    not set
    ...    ${0} > 194    not set
    ...    ${0} > 195    not set
    ...    ${0} > 196    not set
    ...    ${0} > 197    not set
    ...    ${0} > 198    not set
    ...    ${0} > 199    not set
    ...    ${0} > -1    set
    Should Be Equal    ${var}    set
