*** Test Cases ***
List variable as a scalar variable
  @{listvar}=  Set Variable  1  2  3
  Log  ${listvar}

Scalar variable as a list variable
  ${scalar}=   Evaluate  [1,2,3]
  :FOR  ${i}  IN   @{scalar}
  \     Log   ${i}

Scalar variable that can not be a list variable
  ${scalar}=   Set Variable  1
  :FOR  ${i}  IN   @{scalar}
  \     Log   ${i}

None existing scalar variable
  Log  ${scal}

None existing list variable
  Log  @{liss}

