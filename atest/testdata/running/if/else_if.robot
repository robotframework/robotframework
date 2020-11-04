*** Test Cases ***
Else if condition 1 passes
  IF  123 > 23
     Log   passing
  ELSE IF  7 > 3
     Fail  should not be executed
  ELSE
     Fail  should not be executed
  END

Else if condition 2 passes
  IF  3 > 23
     Fail  should not be executed
  ELSE IF  7 > 3
     Log   passing
  ELSE
     Fail  should not be executed
  END

Else if else passes
  IF  1 > 23
     Fail  should not be executed
  ELSE IF  0 > 3
     Fail  should not be executed
  ELSE
     Log   passing
  END

Else if condition 1 failing
  [Documentation]    FAIL expected if fail
  IF  123 > 23
     Fail  expected if fail
  ELSE IF  7 > 3
     Fail  should not be executed
  ELSE
     Fail  should not be executed
  END

Else if condition 2 failing
  [Documentation]    FAIL expected else if fail
  IF  3 > 23
     Fail  should not be executed
  ELSE IF  7 > 3
     Fail  expected else if fail
  ELSE
     Fail  should not be executed
  END

Else if else failing
  [Documentation]    FAIL expected else fail
  IF  1 > 23
     Fail  should not be executed
  ELSE IF  0 > 3
     Fail  should not be executed
  ELSE
     Fail  expected else fail
  END