*** Settings ***
Library           LibraryDecorator.py
Library           LibraryDecoratorWithArgs.py
Library           LibraryDecoratorWithAutoKeywords.py
Library           library_decorator_when_class_and_module_names_do_not_match.py
Library           extend_decorated_library.py
Library           multiple_library_decorators.Class2
Library           multiple_library_decorators.Class3
Library           multiple_library_decorators.py

*** Test Cases ***
Library decorator disables automatic keyword discovery
    [Documentation]    FAIL STARTS: No keyword with name 'Not keyword' found. Did you mean:
    Decorated method is keyword
    Not keyword

Static and class methods when automatic keyword discovery is disabled
    Decorated static method is keyword
    Decorated class method is keyword

Library decorator with arguments disables automatic keyword discovery by default
    [Documentation]    FAIL No keyword with name 'Not keyword v2' found.
    Decorated method is keyword v.2
    Not keyword v2

Library decorator can enable automatic keyword discovery
    Undecorated method is keyword
    Decorated method is keyword as well

When importing a module and there is one decorated class, the class is used as a library
    Class name does not match module name

When importing a module and there are multiple decorated classes, the module is used as a library
    Module keyword

When importing class explicitly, module can have multiple decorated classes
    [Documentation]    FAIL STARTS: No keyword with name 'Class 1 keyword' found. Did you mean:
    Class 2 keyword
    Class 3 keyword
    Class 1 keyword

Imported decorated classes are not considered to be libraries automatically
    Keyword in decorated base class
    Keyword in decorated extending class
