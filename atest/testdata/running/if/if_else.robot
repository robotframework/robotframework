*** Test Cases ***
If passing
   IF  True
       Log   reached this
   END

If failing
   [Documentation]    FAIL failing inside if
   IF  '1' == '1'
       Fail  failing inside if
   END

If not executed
   IF  False
       Fail  should not go here
   END

If not executed failing
  [Documentation]    FAIL after not passing
  IF  'a' == 'b'
      Pass Execution   should go here
  END
  Fail  after not passing

If else - if executed
  IF  1 > 0
      Log   does go through here
  ELSE
      Fail  should not go here
  END

If else - else executed
  IF  0 > 1
      Fail  should not go here
  ELSE
      Log   does go through here
  END

If else - if executed - failing
  [Documentation]    FAIL expected
  IF  1 > 0
      Fail  expected
  ELSE
      Log   unexpected
  END

If else - else executed - failing
  [Documentation]    FAIL expected
  IF  0 > 1
      Log   unexpected
  ELSE
      Fail  expected
  END

If passing in keyword
  Passing if keyword

If passing in else keyword
  Passing else keyword

If failing in keyword
  [Documentation]    FAIL expected
  Failing if keyword

If failing in else keyword
  [Documentation]    FAIL expected
  Failing else keyword

*** Keywords ***
Passing if keyword
  IF  ${1}
     Log  expected
  ELSE IF  12 < 14
     Fail  should not go here
  ELSE
     Fail  not here
  END

Passing else keyword
  IF  ${False}
     Fail  not here
  ELSE
     Log  expected
  END

Failing if keyword
  IF  ${1}
     Fail  expected
  ELSE IF  12 < 14
     Log  should not go here
  ELSE
     Log  not here
  END

Failing else keyword
  IF  ${False}
     Log   should not here
  ELSE
     Fail  expected
  END