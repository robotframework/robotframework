Using C from Robot Framework test libraries
===========================================

This simple example demonstrates how to use C language from Robot
Framework test libraries. The example uses Python's standard ctypes
module (http://docs.python.org/library/ctypes.html), which requires
that the C code is compiled into a shared library. This version is
implemented and tested on Linux, but adapting it to other operating
systems would require only changing compilation and name of the
produced shared library.

The demo application is simple login system that validates user name
and password and prints out are they valid or not. There are two valid
username password combinations: `demo/mode` and `john/long`.

The example consists of four files:

-  `login.c`: The demo application under test
-  `LoginLibrary.py`: Test library that interacts with the demo application
-  `LoginTests.tsv`: Example tests
-  `Makefile`: Used to compile the demo application

To use this example run `make` in the directory where you unzipped the
`robotframework-c-example.zip` package. This will create library
`liblogin.so`, a shared library that is needed to use ctypes
module. Run test by typing:

  pybot LoginTests.tsv

You can also run the application as standalone using command:

  python LoginLibrary.py demo mode

