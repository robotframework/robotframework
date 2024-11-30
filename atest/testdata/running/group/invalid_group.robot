*** Test Cases ***
END missing
    GROUP    This is not closed
        Log   123

Empty GROUP
    GROUP    This is empty
    END
    Log   Last Keyword

Multiple Parameters
    GROUP    Log    123    321
        Fail    this has too much param
    END
    Log   Last Keyword

Non existing var in Name
    GROUP    ${non_existing_var} in Name
        Fail    this has invalid vars in name
    END
    Log   Last Keyword

