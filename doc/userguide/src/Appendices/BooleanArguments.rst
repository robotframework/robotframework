Boolean arguments
=================

Many keywords in Robot Framework `standard libraries`_ accept arguments that
are handled as Boolean values true or false. If such an argument is given as
a string, it is considered false if it is either empty or case-insensitively
equal to `false` or `no`. Other strings are considered true regardless
their value, and other argument types are tested using same `rules as in Python
<http://docs.python.org/2/library/stdtypes.html#truth-value-testing>`__.

Keyword can also accept other special strings than `false` and `no` that are
to be considered false. For example, BuiltIn_ keyword `Should Be True` used
in the examples below considers string `no values` given to its `values`
argument as false.

.. sourcecode:: robotframework

   *** Keywords ***
   True examples
       Should Be Equal    ${x}    ${y}    Custom error    values=True         # Strings are generally true.
       Should Be Equal    ${x}    ${y}    Custom error    values=yes          # Same as the above.
       Should Be Equal    ${x}    ${y}    Custom error    values=${TRUE}      # Python `True` is true.
       Should Be Equal    ${x}    ${y}    Custom error    values=${42}        # Numbers other than 0 are true.

   False examples
       Should Be Equal    ${x}    ${y}    Custom error    values=False        # String `false` is false.
       Should Be Equal    ${x}    ${y}    Custom error    values=no           # Also string `no` is false.
       Should Be Equal    ${x}    ${y}    Custom error    values=${EMPTY}     # Empty string is false.
       Should Be Equal    ${x}    ${y}    Custom error    values=${FALSE}     # Python `False` is false.
       Should Be Equal    ${x}    ${y}    Custom error    values=no values    # Special false string in this context.

Note that prior to Robot Framework 2.9 handling Boolean arguments was
inconsistent. Some keywords followed the above rules, but others simply
considered all non-empty strings, including `false` and `no`, to be true.
