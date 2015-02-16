*** Settings ***
Resource    resource_with_keywords_with_dots_in_name.robot
Resource    resource.with.dots.in.name.robot
Library     library_with_keywords_with_dots_in_name.py
Library     library.with.dots.in.name
Library     library.with.dots

*** Test Cases ***
Dots in keywords in same file
    Dots.in.name
    Dots . In . Name
    multiple...dots..in.a............row
    Multiple ... Dots . . in . A . . . . . . . . . . . . ROW
    Ending with a dot.

Dots in keywords in resource file
    Dots.in.name.in.a.resource
    Multiple...dots . . in . a............row.in.a.resource
    Ending with a dot. In a resource.

Dots in keywords in resource file with full name
    resource_with_keywords_with_dots_in_name.Dots.in.name.in.a.resource
    resource_with_keywords_with_dots_in_name.Multiple...dots . . in . a............row.in.a.resource
    resource_with_keywords_with_dots_in_name.Ending with a dot. In a resource.

Dots in keywords in library
    Dots.in.name.in.a.library
    Multiple...dots . . in . a............row.in.a.library
    Ending with a dot. In a library.

Dots in keywords in library with full name
    library_with_keywords_with_dots_in_name.Dots.in.name.in.a.library
    library_with_keywords_with_dots_in_name.Multiple...dots . . in . a............row.in.a.library
    library_with_keywords_with_dots_in_name.Ending with a dot. In a library.

Dots in resource name
    No dots in keyword name in resource with dots in name

Dots in resource name with full name
    resource.with.dots.in.name.No dots in keyword name in resource with dots in name

Dots in resource name and keyword name
    Dots.in.name.in.a.resource.with.dots.in.name
    Multiple...dots . . in . a............row.in.a.resource.with.dots.in.name
    Ending with a dot. In a resource with dots in name.

Dots in resource name and keyword name with full name
    resource.with.dots.in.name.Dots.in.name.in.a.resource.with.dots.in.name
    resource.with.dots.in.name.Multiple...dots . . in . a............row.in.a.resource.with.dots.in.name
    resource.with.dots.in.name.Ending with a dot. In a resource with dots in name.

Dots in library name
    No dots in keyword name in library with dots in name

Dots in library name with full name
    library.with.dots.in.name.No dots in keyword name in library with dots in name

Dots in library name and keyword name
    Dots.in.name.in.a.library.with.dots.in.name
    Multiple...dots . . in . a............row.in.a.library.with.dots.in.name
    Ending with a dot. In a library with dots in name.

Dots in library name and keyword name with full name
    library.with.dots.in.name.Dots.in.name.in.a.library.with.dots.in.name
    library.with.dots.in.name.Multiple...dots . . in . a............row.in.a.library.with.dots.in.name
    library.with.dots.in.name.Ending with a dot. In a library with dots in name.

Conflicting names with dots
    [Documentation]    This conflict cannot be resolved    FAIL
    ...    Multiple keywords with name 'library.with.dots.in.name.Conflict' found:
    ...    ${SPACE*4}library.with.dots.In.name.conflict
    ...    ${SPACE*4}library.with.dots.in.name.Conflict
    Conflict                              # in 'library.with.dots.in.name'
    in.name.Conflict                      # in 'library.with.dots'
    library.with.dots.in.name.Conflict    # matches both of the above

*** Keywords ***
Dots.in.name
    No operation

Multiple...dots . . in . a............row
    No operation

Ending with a dot.
    No operation
