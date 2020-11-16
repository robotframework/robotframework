*** Test Cases ***
Else errors
  IF  'mars' == 'maa'
     Log   something
  ELSE  ${True}
     Log   ok
  END