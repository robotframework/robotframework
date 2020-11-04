*** Test Cases ***
Invalid else after else
  IF  ${False}
      Log   something
  ELSE
      Log   something
  ELSE
      Log   something
  END