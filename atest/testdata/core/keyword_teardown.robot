*** Test Cases ***

Passing Keyword with Teardown
    Keyword with Teardown

Failing Keyword with Teardown
    [Documentation]  FAIL Expected Failure!
    Failing Keyword with Teardown

Teardown in Keyword with Embedded Arguments
    [Documentation]  FAIL Expected Failure in UK with Embedded Arguments
    Keyword with Teardown and Embedded Arguments
    Failing Keyword with Teardown and Embedded Arguments

Failure in Keyword Teardown
    [Documentation]  FAIL Keyword teardown failed:\nFailing in UK Teardown
    Failure in Keyword Teardown
    Fail  This should never be run

Failures in Keyword and Teardown
    [Documentation]  FAIL Expected Failure!\n\nAlso keyword teardown failed:\nFailing in UK Teardown
    Failures in Keyword and Teardown

Multiple Failures in Keyword Teardown
    [Documentation]  FAIL Keyword teardown failed:\nSeveral failures occurred:\n\n1) Failure in Teardown\n\n2) Expected Failure!\n\n3) Third failure in Teardown
    Multiple Failures in Keyword Teardown

Nested Keyword Teardowns
    Nested Keyword Teardowns

Nested Keyword Teardown Failures
    [Documentation]  FAIL Keyword teardown failed:\nFailing in UK Teardown\n\nAlso keyword teardown failed:\nFailing in outer UK Teardown
    Nested Keyword Teardown Failures

Continuable Failure in Keyword
    [Documentation]  FAIL Please continue
    Continuable Failure in Keyword

Non-ASCII Failure in Keyword Teardown
    [Documentation]  FAIL Keyword teardown failed:\nHyvää äitienpäivää!
    Non-ASCII Failure in Keyword Teardown

Keyword cannot have only teardown
    [Documentation]  FAIL User keyword cannot be empty.
    Keyword cannot have only teardown

Replacing Variables in Keyword Teardown Fails
    [Documentation]  FAIL Keyword teardown failed:\nVariable '${NON EXISTING}' not found.
    Replacing Variables in Keyword Teardown Fails


*** Keywords ***
Keyword with Teardown
    Log  In UK
    [Teardown]  Log  In UK Teardown

Failing Keyword with Teardown
    Fail  Expected Failure!
    Log   Executed if in nested Teardown
    [Teardown]  Log  In Failing UK Teardown

Keyword with Teardown and ${embedded} ${arguments:A.*}
    Log  In UK with ${embedded} ${arguments}
    [Teardown]  Log  In Teardown of UK with ${embedded} ${arguments}

Failing Keyword with Teardown and ${embedded} ${arguments:[Aa].*}
    Fail  Expected Failure in UK with ${embedded} ${arguments}
    [Teardown]  Log  In Teardown of Failing UK with ${embedded} ${arguments}

Failure in Keyword Teardown
    Log  In UK
    [Teardown]  Fail  Failing in UK Teardown

Failures in Keyword and Teardown
    Fail  Expected Failure!
    [Teardown]  Fail  Failing in UK Teardown

Nested Keyword Teardowns
    Keyword with Teardown
    [Teardown]  Keyword with Teardown

Nested Keyword Teardown Failures
    Failure in Keyword Teardown
    [Teardown]  Fail  Failing in outer UK Teardown

Continuable Failure in Keyword
    Run Keyword and Continue on Failure  Fail  Please continue
    Log  After continuable failure
    [Teardown]  Log  In UK Teardown

Multiple Failures in Keyword Teardown
    Log  In UK
    [Teardown]  Multiple Failures

Multiple Failures
    Fail  Failure in Teardown
    Failing keyword with Teardown
    Fail  Third failure in Teardown

Non-ASCII Failure in Keyword Teardown
    Log  åäö
    [Teardown]  Fail  Hyvää äitienpäivää!

Keyword cannot have only teardown
    [Teardown]  Fail  This is not executed

Replacing Variables in Keyword Teardown Fails
    Log  In UK
    [Teardown]  ${NON EXISTING}
