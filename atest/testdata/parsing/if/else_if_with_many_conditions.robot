*** Test Cases ***
Else If errors
  IF  'mars' == 'maa'
     Log   something
  ELSE IF  ${False}  ${True}
     Log  nothing
  ELSE
     Log   ok
  END