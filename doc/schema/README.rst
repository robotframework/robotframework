Robot Framework and Libdoc XML schemas
======================================

Introduction
------------

While Robot Framework is running tests, it generates an XML output file
containing all information about the execution. After execution is over it
creates, by default, log and report files using the `Rebot tool`__
internally. The same ``rebot`` functionality can also be used externally
afterwards both as a standalone tool and programmatically__.

This document describes the format of the output file in high level and in the
same folder there are detailed
`XML schema definition <http://en.wikipedia.org/wiki/XML_Schema_(W3C)>`_ (XSD)
files that can be used for validating that an XML file is Robot Framework
compatible. The output file format can be useful both for people interested in
parsing the output and for people interested to create Robot Framework
compatible outputs.

Also Robot Framework's library documentation tool Libdoc__ can generate output
in XML format and this directory contains a schema documentation for it as
well.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#rebot
__ http://robot-framework.readthedocs.org/en/latest/autodoc/robot.html#robot.rebot.rebot
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#libdoc

Schema definitions
------------------

Available schema files:

  * `<robot-xsd10.xsd>`__ - Robot Framework XML output (XSD 1.0 compatible version)
  * `<robot-xsd11.xsd>`__ - Robot Framework XML output (XSD 1.1 compatible version)
  * `<libdoc.01.xsd>`__ - Libdoc XML spec version 1 (Robot Framework < 3.2) (XSD 1.0)
  * `<libdoc.02.xsd>`__ - Libdoc XML spec version 2 (Robot Framework >= 3.2) (XSD 1.0)

XSD 1.1 schemas are more complete than XSD 1.0 schemas but not as widely
supported.

General Robot Framework XML output structure
--------------------------------------------

These are the main elements in Robot Framework XML output files with descriptions of their
sub-elements. Unless stated otherwise, all attributes are optional. Additionally
``rebot`` does not care of the order of the XML elements, except for the order
of suite, test, and kw elements. Starting from Robot Framework 2.9, empty
elements and attributes are not written to the output XML. This means that,
for example, test case having no documentation has no ``<doc>`` element either.

robot - root element
    * ``suite`` - root element always has one suite which contains the subsuites and tests
    * ``statistics`` - statistics contains statistics of the test run
    * ``errors`` - if there were any errors, they are listed in this element

suite - suite element, name is given as an attribute
    * ``kw`` - suite can have two kw elements: setup and teardown, both are optional
    * ``suite`` - any number of sub suites in execution order
    * ``test`` - any number of tests in execution order
    * ``doc`` - optional documentation element
    * ``metadata`` - optional suite metadata
    * ``status`` - suite has to have a status element

test - test element, name is given as an attribute
    * ``kw`` - keywords of the test in execution order
    * ``msg`` - optional test message
    * ``doc`` - optional test documentation
    * ``tags`` - optional test tags
    * ``timeout`` - optional test timeout. Before 3.0 this was an attribute.
    * ``status`` - test has to have a status

kw - keyword element, name is given as an attribute. Type attribute describes the type of keyword. If this attribute is not present, type is assumed to be ``kw``.
    * ``tags`` - optional keyword tags (new in 2.9)
    * ``doc`` - optional keyword documentation
    * ``arguments`` - optional keyword arguments
    * ``assignment`` - possible assignment of keyword's return values to variables, each variable in ``var`` subelement (new in 2.9)
    * ``kw`` - possible sub-keywords in execution order
    * ``msg`` - any number of optional keyword messages
    * ``timeout`` - optional keyword timeout. Before 3.0 this was an attribute.
    * ``status`` - keyword has to have a status

For more details and full list of elements and attributes, please see the XML schema files above.
