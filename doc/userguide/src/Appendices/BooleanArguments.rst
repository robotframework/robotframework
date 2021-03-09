Boolean arguments
=================

Many keywords in Robot Framework `standard libraries`_ accept arguments that
are handled as Boolean values true or false. If such an argument is given as
a string, it is considered false if it is an empty string or equal to
`FALSE`, `NONE`, `NO`, `OFF` or `0`, case-insensitively. Other
strings are considered true unless the keyword documentation explicitly
states otherwise, and other argument types are tested using the same
`rules as in Python`__.

__ http://docs.python.org/library/stdtypes.html#truth-value-testing

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
       Should Be Equal    ${x}    ${y}    Custom error    values=no values    # Special false string with this keyword.

.. note:: Considering `OFF` and `0` false is new in Robot Framework 3.1.
