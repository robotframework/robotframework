*** Variables ***
${NOOP}  No Operation
@{MANY ARGUMENTS}  hello  1  2  3
@{ESCAPED}  1  \AND  2  Log Many  x\${escaped}  c:\\temp
@{LIST VARIABLE}  Log Many  this  AND  that
${AND VARIABLE}  AND


*** Test Cases ***
with arguments
    Run Keywords  Should Be Equal  2  2  AND  No Operation  AND  Log Many  hello  1  2  3  AND  Should Be Equal  1  1

Should fail with failing keyword
    [Documentation]  FAIL  1 != 2
    Run Keywords  No Operation  AND  Should Be Equal  1  2  AND  Not Executed

Should support keywords and arguments from variables
    Run Keywords  Should Be Equal  2  2  AND  ${NOOP}  AND  Log Many  @{MANY ARGUMENTS}  AND  Should Be Equal As Integers  ${1}  1

AND must be upper case
    [Documentation]  FAIL  No keyword with name 'no kw' found.
    Run Keywords  Log Many  this  and  that  AND  no kw

AND must be whitespace sensitive
    [Documentation]  FAIL  No keyword with name 'no kw' found.
    Run Keywords  Log Many  this  A ND  that  AND  no kw

Escaped AND
    [Documentation]  FAIL  No keyword with name 'no kw' found.
    Run Keywords  Log Many  this  \AND  that  AND  no kw

AND from Variable
    [Documentation]  FAIL  No keyword with name 'no kw' found.
    Run Keywords  Log Many  this  ${AND VARIABLE}  that  AND  no kw

AND in List Variable
    [Documentation]  FAIL  No keyword with name 'no kw' found.
    Run Keywords  @{LIST VARIABLE}  AND  no kw

Escapes in List Variable should be handled correctly
    [Documentation]  FAIL  No keyword with name 'no kw' found.
    Run Keywords  Log Many  @{ESCAPED}  AND  no kw

AND as last argument should raise an error
    [Documentation]  FAIL  Incorrect use of AND
    Run Keywords  Log Many  1  2  AND  No Operation  AND

Consecutive AND's
    [Documentation]  FAIL  Incorrect use of AND
    Run Keywords  Log Many  1  2  AND  AND  No Operation

AND as first argument should raise an error
    [Documentation]  FAIL  Incorrect use of AND
    Run Keywords  AND  Log Many  1  2
