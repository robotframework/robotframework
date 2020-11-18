*** Test Cases ***
If without condition
    [Documentation]    FAIL 'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
    IF
       No Operation
    END

If with many conditions
    [Documentation]    FAIL 'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
    IF   '1' == '1'  '2' == '2'  '3' == '3'
       No Operation
    END

If without end
    [Documentation]    FAIL IF has no closing 'END'.
    IF  ${True}
       No Operation

If with wrong case
   [Documentation]    FAIL 'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
   if  ${True}
       Log  hello
   END

Else if without condition
   [Documentation]    FAIL after not passing
   IF  'mars' == 'maa'
      Log   something
   ELSE IF
      Log  nothing
   ELSE
      Log   ok
   END

Else if with multiple conditions
  [Documentation]    FAIL after not passing
  IF  'mars' == 'maa'
     Log   something
  ELSE IF  ${False}  ${True}
     Log  nothing
  ELSE
     Log   ok
  END

Else with a condition
  [Documentation]    FAIL after not passing
  IF  'mars' == 'maa'
     Log   something
  ELSE  ${True}
     Log   ok
  END

If with empty if
  [Documentation]    FAIL IF has empty body.
  IF  'jupiter' == 'saturnus'
  END

If with empty else
  [Documentation]    FAIL after not passing
  IF  'kuu' == 'maa'
     Log   something
  ELSE
  END

If with empty else_if
  [Documentation]    FAIL after not passing
  IF  'mars' == 'maa'
     Log   something
  ELSE IF  ${False}
  ELSE
     Log   ok
  END