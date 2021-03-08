Robot Framework and Libdoc schema definitions
=============================================

Introduction
------------

This directory contains schema definitions for Robot Frameworks output.xml files
as well as for spec files created by Libdoc_.

output.xml schema
-----------------

While Robot Framework is running tests, it generates an XML output file
containing all information about the execution. After execution is over it
creates, by default, log and report files based on the output.xml file.
Logs and reports can be generated also afterwards both using the standalone
Rebot_ tool and programmatically__. The output.xml file format can be useful
both for people interested in parsing the output and for people interested
to create Robot Framework compatible outputs.

This directory contains XSD_ schema definitions that are compatible with
different Robot Framework versions. Newer output.xml files have ``schemaversion``
attribute telling which version they support and older implicitly support schema
version 1.

  * `<robot.02.xsd>`__ - Compatible with Robot Framework >= 4.0.
  * `<robot.01.xsd>`__ - Compatible with Robot Framework < 4.0.

Due to XSD 1.1 not being widely adopted, these schema definitions use XSD 1.0.
Newer schema definitions contain embedded documentation and comments explaining
the structure in more detail. They also contain instructions how to make them
XSD 1.1 compatible if needed.

.. _Rebot: http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#rebot
__ http://robot-framework.readthedocs.org/en/latest/autodoc/robot.html#robot.rebot.rebot
.. _XSD: http://en.wikipedia.org/wiki/XML_Schema_(W3C)

Libdoc schema
-------------

Libdoc_ tool distributed with Robot Framework can generate machine readable spec files
both in XML and JSON format. XML spec files have XSD_ 1.0 compatible schema definition
and JSON spec schema is JSON Schema `DRAFT-7`__ compatible.

  * `<libdoc.03.xsd>`__ - Compatible with Robot Framework >= 4.0.
  * `<libdoc.02.xsd>`__ - Compatible with Robot Framework == 3.2.
  * `<libdoc.01.xsd>`__ - Compatible with Robot Framework < 3.2.
  * `<libdoc_schema.json>`__ - Compatible with Robot Framework >= 4.0.

.. _Libdoc: http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#libdoc
__ https://json-schema.org/specification-links.html#draft-7

Testing schemas
---------------

Both output.xml and Libdoc schema definitions are tested as part of `acceptance test
runs <../../atest/README.rst>`__ by validating created outputs against the appropriate
schemas. Most output.xml files created during test runs are not validated, however,
because that would slow down test execution a bit too much. Full validation `can be
enabled separately`__ and that should be done if the schema is updated or output.xml
structure is changed.

__ https://github.com/robotframework/robotframework/blob/master/atest/README.rst#schema-validation
