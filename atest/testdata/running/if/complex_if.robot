*** Test Cases ***
Multiple keywords in if
   ${calculator}=  Set Variable  1
   IF  'kuu on taivaalla'
      ${calculator}=  Evaluate  1+${calculator}
      ${calculator}=  Evaluate  1+${calculator}
      ${calculator}=  Evaluate  1+${calculator}
   END
   Should be equal  ${calculator}  ${4}

Nested ifs
   ${calculator}=  Set Variable  1
   IF  'kuu on taivaalla taas'
      ${calculator}=  Evaluate  1+${calculator}
      IF  'sininen on taivas'
            ${calculator}=  Evaluate  3+${calculator}
      ELSE
            ${calculator}=  Evaluate  10+${calculator}
      END
      IF  ${False}
            ${calculator}=  Evaluate  2+${calculator}
      END
      ${calculator}=  Evaluate  1+${calculator}
   END
   Should be equal  ${calculator}  ${6}

If inside for loop
   ${outerval}=  Set Variable  wrong
   FOR  ${var}  IN  1  2  3
       IF  ${var} == 2
          ${outerval}=  Set Variable  ${var}
       END
   END
   Should be equal  ${outerval}  2

Setting after if
   ${var}=  Set Variable  not found
   IF  'something'
      ${var}=  Set Variable  found
   END
   [Teardown]  Log  Teardown was ${var} and executed.

For loop inside if
   ${value}   Set Variable   0
   IF  'kaunis maailma'
        FOR  ${var}  IN  1  2  3
            ${value}=   Set Variable  ${var}
        END
   ELSE IF  'ei tanne'
        ${value}=  Set Variable  123
   END
   Should be equal  ${value}  3

For loop inside for loop
   ${checker}  Set Variable  wrong
   FOR  ${first}  IN  1  2  3
      FOR  ${second}  IN  4  5  6
          ${checker}  Set Variable  ${first} - ${second}
      END
   END
   Should be equal  ${checker}  3 - 6

Direct Boolean condition
   [Documentation]  PASS From the condition
   IF  ${True}
      Pass Execution  From the condition
   END
   Fail  condition not working

Direct Boolean condition false
   IF  ${False}
      Fail  should not execute
   END

Nesting insanity
   ${assumption}  Set Variable  is wrong
   IF  ${True}
      FOR  ${iter}  IN  1  2  3
         IF  ${iter} == 1
             ${assumption}  Set Variable  2 5 9 8
         END
         IF  ${iter} == 2
             FOR  ${iter2}  IN  4  5  6
                 IF  ${iter2} == 5
                     FOR  ${iter3}  IN  7  8  9
                         ${assumption}  Set Variable  ${assumption} ${iter3}
                     END
                     ${assumption}  Set Variable  ${assumption} ${iter2}
                 END
             END
             ${assumption}  Set Variable  ${assumption} ${iter}
         END
      END
   END
   Should be equal  ${assumption}  2 5 9 8 7 8 9 5 2

For loop if else early exit
  [Documentation]  PASS From the condition
  FOR  ${iter1}  IN  1  2  3
     IF   1 > 2
         Fail   should not execute if branch
     ELSE
         Pass Execution  From the condition
     END
  END
  Fail  should not execute end of test

For loop if else if early exit
  [Documentation]  PASS From the condition
  FOR  ${iter1}  IN  1  2  3
     IF   1 > 2
         Fail   should not execute if branch
     ELSE IF  ${iter1} == 2
         Pass Execution  From the condition
     END
  END
  Fail  should not execute end of test

Recursive if
   Recurse  1

If creating variable
   ${outer}=  Set Variable  before
   IF  ${True}
      ${var}=     Set Variable  expected
      ${outer}=   Set Variable  inside
   END
   Should be equal  ${var}  expected
   Should be equal  ${outer}  inside

If inside if
   IF  ${True}
      IF  ${False}
          Fail  stupid but possible
      END
   ELSE IF  ${True}
      IF  ${False}
          Fail  stupid but possible
      END
   ELSE
      IF  ${False}
          Fail  stupid but possible
      END
   END

*** Keywords ***
Recurse
   [Arguments]  ${value}
   IF  ${value} < 1000
       Recurse  ${value}0
   END