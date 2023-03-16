*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/invalid_try_except.robot
Test Template     Verify try except and block statuses

*** Test Cases ***
TRY without END
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN

TRY without body
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN

TRY without EXCEPT or FINALLY
    TRY:FAIL

TRY with ELSE without EXCEPT or FINALLY
    TRY:FAIL    ELSE:NOT RUN

TRY with argument
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN

EXCEPT without body
    TRY:FAIL    EXCEPT:NOT RUN    EXCEPT:NOT RUN    FINALLY:NOT RUN

Default EXCEPT not last
    TRY:FAIL    EXCEPT:NOT RUN    EXCEPT:NOT RUN    FINALLY:NOT RUN

Multiple default EXCEPTs
    TRY:FAIL    EXCEPT:NOT RUN    EXCEPT:NOT RUN    ELSE:NOT RUN

AS requires variable
    TRY:FAIL    EXCEPT:NOT RUN

AS accepts only one variable
    TRY:FAIL    EXCEPT:NOT RUN

Invalid AS variable
    TRY:FAIL    EXCEPT:NOT RUN

ELSE with argument
    TRY:FAIL    EXCEPT:NOT RUN    ELSE:NOT RUN    FINALLY:NOT RUN

ELSE without body
    TRY:FAIL    EXCEPT:NOT RUN    ELSE:NOT RUN    FINALLY:NOT RUN

Multiple ELSE blocks
    TRY:FAIL    EXCEPT:NOT RUN    ELSE:NOT RUN    ELSE:NOT RUN    FINALLY:NOT RUN

FINALLY with argument
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN

FINALLY without body
    TRY:FAIL    FINALLY:NOT RUN

Multiple FINALLY blocks
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN    FINALLY:NOT RUN

ELSE before EXCEPT
    TRY:FAIL    EXCEPT:NOT RUN    ELSE:NOT RUN    EXCEPT:NOT RUN   FINALLY:NOT RUN

FINALLY before EXCEPT
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN    EXCEPT:NOT RUN

FINALLY before ELSE
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN    ELSE:NOT RUN

Template with TRY
    TRY:FAIL    EXCEPT:NOT RUN

Template with TRY inside IF
    TRY:FAIL    EXCEPT:NOT RUN    path=body[0].body[0].body[0]

Template with IF inside TRY
    TRY:FAIL    FINALLY:NOT RUN

BREAK in FINALLY
    TRY:PASS    FINALLY:FAIL    path=body[0].body[0].body[0]

CONTINUE in FINALLY
    TRY:PASS    FINALLY:FAIL    path=body[0].body[0].body[0]

RETURN in FINALLY
    TRY:PASS    FINALLY:FAIL    path=body[0].body[0]

Invalid TRY/EXCEPT causes syntax error that cannot be caught
    TRY:FAIL    EXCEPT:NOT RUN    ELSE:NOT RUN

Dangling FINALLY
    [Template]    Check Test Case
    ${TEST NAME}
