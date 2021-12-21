*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/invalid_try_except.robot
Test Template     Verify try except and block statuses

*** Test Cases ***
Try without END
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN

Try without body
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN

Try without except or finally
    TRY:FAIL

Try with argument
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN

Except without body
    TRY:FAIL    EXCEPT:NOT RUN    EXCEPT:NOT RUN    FINALLY:NOT RUN

Default except not last
    TRY:FAIL    EXCEPT:NOT RUN    EXCEPT:NOT RUN    FINALLY:NOT RUN

Multiple default excepts
    TRY:FAIL    EXCEPT:NOT RUN    EXCEPT:NOT RUN    TRY ELSE:NOT RUN

AS not the second last token
    TRY:FAIL    EXCEPT:NOT RUN

Invalid AS variable
    TRY:FAIL    EXCEPT:NOT RUN

Else with argument
    TRY:FAIL    EXCEPT:NOT RUN    TRY ELSE:NOT RUN    FINALLY:NOT RUN

Else without body
    TRY:FAIL    EXCEPT:NOT RUN    TRY ELSE:NOT RUN    FINALLY:NOT RUN

Multiple else blocks
    TRY:FAIL    EXCEPT:NOT RUN    TRY ELSE:NOT RUN    TRY ELSE:NOT RUN    FINALLY:NOT RUN

Finally with argument
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN

Finally without body
    TRY:FAIL    FINALLY:NOT RUN

Multiple finally blocks
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN    FINALLY:NOT RUN

Else before except
    TRY:FAIL    EXCEPT:NOT RUN    TRY ELSE:NOT RUN    EXCEPT:NOT RUN   FINALLY:NOT RUN

Finally before except
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN    EXCEPT:NOT RUN

Finally before else
    TRY:FAIL    EXCEPT:NOT RUN    FINALLY:NOT RUN    TRY ELSE:NOT RUN

Template with try except
    TRY:FAIL    EXCEPT:NOT RUN

Template with try except inside if
    TRY:FAIL    EXCEPT:NOT RUN    path=body[0].body[0].body[0]

Template with IF inside TRY
    TRY:FAIL    FINALLY:NOT RUN
