*** Test Cases ***
END missing
    [Documentation]    FAIL    GROUP must have closing END.
    GROUP    This is not closed
        Fail    Not run

Empty
    [Documentation]    FAIL    GROUP cannot be empty.
    GROUP    This is empty
    END
    Log    Outside

Multiple parameters
    [Documentation]    FAIL    GROUP accepts only one argument as name, got 3 arguments 'Too', 'many' and 'values'.
    GROUP    Too    many    values
        Fail    Not run
    END
    Log   Last Keyword

Non-existing variable in name
    [Documentation]    FAIL    Variable '\${non_existing_var}' not found.
    GROUP    ${non_existing_var} in name
        Fail    Not run
    END
    Log   Last Keyword

Invalid data is not reported after failures
    [Documentation]    FAIL    Something bad happened!
    # We probably should validate syntax before even executing the test and report
    # such failures early. That should then be done also with other control structures.
    Fail    Something bad happened!
    GROUP    ${non_existing_non_executed_variable_is_ok}
        Fail    Not run
    END
    GROUP    Empty non-executed GROUP is ok
    END
    GROUP    Even missing END is ok
        Fail    Not run
