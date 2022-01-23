*** Settings ***
Resource        resource.robot

*** Test Cases ***
IF will not recurse in dry run
    Recursive if  call again
    This is validated

ELSE IF will not recurse in dry run
    Recursive else if  call againdry/if
    This is validated

ELSE will not recurse in dry run
    Recursive else  call again
    This is validated

Dryrun fail inside of IF
    [Documentation]    FAIL    Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 2.
    IF  'something' == 'thing'
       Anarchy in the UK    1    2
    END
    This is validated

Dryrun fail inside of ELSE IF
    [Documentation]    FAIL    Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 1.
    IF  'total' == 'empty'
       Log  this is fine
    ELSE IF  'something' == 'thing'
       Anarchy in the UK    1
    ELSE
       Log  fine and dandy
    END
    This is validated

Dryrun fail inside of ELSE
    [Documentation]    FAIL    Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 0.
    IF  'total' == 'empty'
       Log  this is fine
    ELSE
       Anarchy in the UK
    END
    This is validated

Dryrun fail invalid IF in non executed branch
    [Documentation]    FAIL    IF must have a condition.
    IF  1 > 2
       Keyword with invalid if
    END
    This is validated

Dryrun fail invalid ELSE in non executed branch
    [Documentation]    FAIL    ELSE does not accept arguments, got '\${False}'.
    IF  1 > 0
       No operation
    ELSE
       Keyword with invalid else
    END
    This is validated

Dryrun fail invalid ELSE IF in non executed branch
    [Documentation]    FAIL    ELSE IF must have a condition.
    IF  'fortran' == 'cobol'
       Keyword with invalid else if
    END
    This is validated

Dryrun fail empty IF in non executed branch
    [Documentation]    FAIL    IF branch cannot be empty.
    IF  ${True}
       Log  hello
    ELSE IF  ${True}
       Keyword with empty if
    END
    This is validated

*** Keywords ***
Keyword with invalid if
    IF
       Log  invalid
    END

Keyword with invalid else
    IF  ${True}
       Log  invalid
    ELSE  ${False}
       Log  invalid
    END

Keyword with invalid else if
    IF  ${True}
       Log  invalid
    ELSE IF
       Log  invalid
    END

Keyword with empty if
   IF  ${False}
   END

Recursive if
    [Arguments]  ${arg}
    IF  '${arg}' == 'call again'
      Recursive if  call no more
    ELSE IF  '${arg}' == 'call sometimes'
      Log  no more calls
    ELSE
      Log  no more calls
    END

Recursive else if
    [Arguments]  ${arg}
    IF  '${arg}' == 'call no more'
      Log  no more calls
    ELSE IF  '${arg}' == 'call again'
      Recursive else if  call no more
    ELSE
      Log  no more calls
    END

Recursive else
    [Arguments]  ${arg}
    IF  '${arg}' == 'call no more'
      Log  no more calls
    ELSE IF  '${arg}' == 'call sometimes'
      Log  no more calls
    ELSE
      Recursive else  call no more
    END
