Extending the Robot Framework Jar
=================================

Adding additional test libraries or support code to the Robot Framework jar is
quite straightforward using the ``jar`` command included in standard JDK
installation. Python code must be placed in :file:`Lib` directory inside
the jar and Java code can be placed directly to the root of the jar, according
to package structure.

For example, to add Python package `mytestlib` to the jar, first copy the
:file:`mytestlib` directory under a directory called :file:`Lib`, then run
following command in the directory containing :file:`Lib`::

  jar uf /path/to/robotframework-2.7.1.jar Lib

To add compiled java classes to the jar, you must have a directory structure
corresponding to the Java package structure and add that recursively to the
zip.

For example, to add class `MyLib.class`, in package `org.test`,
the file must be in :file:`org/test/MyLib.class` and you can execute::

  jar uf /path/to/robotframework-2.7.1.jar org
