*** Test Cases ***
If without condition
    [Documentation]    FAIL    IF has no condition.
    IF
       No Operation
    END

If with many conditions
    [Documentation]    FAIL    IF has more than one condition.
    IF   '1' == '1'  '2' == '2'  '3' == '3'
       No Operation
    END

If without end
    [Documentation]    FAIL    IF has no closing END.
    IF  ${True}
       No Operation

Invalid END
    [Documentation]    FAIL    END does not accept arguments.
    IF    True
        Fail    Not executed
    END    this    is    invalid

If with wrong case
   [Documentation]    FAIL    'If' is a reserved keyword. It must be an upper case 'IF' when used as a marker.
   if  ${True}
       Log  hello
   END

Else if without condition
   [Documentation]    FAIL    ELSE IF has no condition.
   IF  'mars' == 'mars'
      Log   something
   ELSE IF
      Log  nothing
   ELSE
      Log   ok
   END

Else if with multiple conditions
  [Documentation]    FAIL    ELSE IF has more than one condition.
  IF  'maa' == 'maa'
     Log   something
  ELSE IF  ${False}  ${True}
     Log  nothing
  ELSE
     Log   ok
  END

Else with a condition
  [Documentation]    FAIL    ELSE has condition.
  IF  'venus' != 'mars'
     Log   something
  ELSE  ${True}
     Log   ok
  END

If with empty if
  [Documentation]    FAIL    IF has empty body.
  IF  'jupiter' == 'saturnus'
  END

If with empty else
  [Documentation]    FAIL    ELSE has empty body.
  IF  'kuu' == 'maa'
     Log   something
  ELSE
  END

If with empty else_if
  [Documentation]    FAIL    ELSE IF has empty body.
  IF  'mars' == 'maa'
     Log   something
  ELSE IF  ${False}
  ELSE
     Log   ok
  END

If with else after else
  [Documentation]    FAIL     Multiple ELSE branches.
  IF  'kuu' == 'maa'
     Log   something
  ELSE
     Log   hello
  ELSE
     Log   hei
  END

If with else if after else
  [Documentation]    FAIL    ELSE IF after ELSE.
  IF  'kuu' == 'maa'
     Log   something
  ELSE
     Log   hello
  ELSE IF  ${True}
     Log   hei
  END

If for else if parsing
   [Documentation]    FAIL    ELSE IF after ELSE.
   FOR  ${value}  IN  1  2  3
       IF  ${value} == 1
           Log  ${value}
       ELSE
           No Operation
       ELSE IF  ${value} == 3
           Log  something
       END
   END

Multiple errors
    [Documentation]    FAIL
    ...    Multiple errors:
    ...    - IF has no condition.
    ...    - IF has empty body.
    ...    - ELSE IF after ELSE.
    ...    - Multiple ELSE branches.
    ...    - IF has no closing END.
    ...    - ELSE IF has more than one condition.
    ...    - ELSE IF has empty body.
    ...    - ELSE has condition.
    ...    - ELSE has empty body.
    ...    - ELSE IF has no condition.
    ...    - ELSE IF has empty body.
    ...    - ELSE has empty body.
    IF
    ELSE IF    too    many
    ELSE   oops
    ELSE IF
    ELSE
