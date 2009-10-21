Example of writing Robot Framework test library in C
====================================================

This simple example how to use C libraries with Robot Framework (RF) in Linux
environment. The application is validating user name and password and prints
out is the login successful or not. There are two valid username password
combinations demo mode and john long.

The example consists of four files:

-  `login.c`: Application that will be tested using RF
-  `LoginLibrary.py`: Python interface to C library
-  `LoginTests.tsv`: Tests that run against C library
-  `Makefile`: Used to compile the C file

To use this example run `make` in the directory where you unzipped the
`robotframework-c-example.zip` package. This will create library `liblogin.so`, a shared
library that is needed to use ctypes python module. Run test by typing::

  pybot LoginTests.tsv

You can run the application as standalone using e.g. command::

  python LoginLibrary.py demo mode
