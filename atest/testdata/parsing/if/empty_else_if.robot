*** Test Cases ***
Invalid empty else if
  IF  'mars' == 'maa'
     Log   something
  ELSE IF  ${False}
  ELSE
     Log   ok
  END