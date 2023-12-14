Robot Framework and Libdoc schema definitions
=============================================

This directory contains schema definitions for various Robot Framework and
Libdoc_ output files.

Only the latest schema versions are directly available and they may not be
compatible with older Robot Framework versions. If you need to access old
schema files, switch to an appropriate version control tag using the selector
at the top of the page.

Schema files
------------

- `<robot.xsd>`_ - Robot Framework XML output schema in XSD_ format.
- `<running.json>`_ - `JSON Schema`_ for ``robot.running.TestSuite`` model structure.
- `<result.json>`_ - `JSON Schema`_ for ``robot.result.TestSuite`` model structure.
- `<libdoc.xsd>`_ - Libdoc XML spec schema in XSD_ format.
- `<libdoc.json>`_ - Libdoc JSON spec schema in `JSON Schema`_ format.

Schema standard versions
------------------------

XML schema definitions use XSD 1.0 due to XSD 1.1 not being widely adopted.
Schema files themselves contain embedded documentation and comments explaining
the structure in more detail. They also contain instructions how to make them
XSD 1.1 compatible if needed.

JSON schemas use JSON Schema Draft 2020-12.

Updating schemas
----------------

XSD schemas are created by hand and updates need to be done directly to them.

JSON schemas are generated based on models created using pydantic_.
To modify these schemas, first update the appropriate pydantic model either
in `<running_json_schema.py>`_, `<result_json_schema.py>`_, or `<libdoc_json_schema.py>`_
and then execute that file to regenerate the actual schema file in
`<running.json>`_, `<result.json>`_, or `<libdoc.json>`_, respectively.

Testing schemas
---------------

Schema definitions are tested as part of `acceptance test runs <../../atest/README.rst>`__
by validating created outputs against the appropriate schemas. Most output.xml
files created during test runs are not validated, however, because that would
slow down test execution a bit too much. Full validation `can be enabled separately`__
and that should be done if the schema is updated or output.xml structure is changed.

.. _Libdoc: http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#libdoc
.. _XSD: http://en.wikipedia.org/wiki/XML_Schema_(W3C)
.. _JSON Schema: https://json-schema.org
.. _pydantic: https://pydantic-docs.helpmanual.io/usage/schema
__ https://github.com/robotframework/robotframework/blob/master/atest/README.rst#schema-validation
