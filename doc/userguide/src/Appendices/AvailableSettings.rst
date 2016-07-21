All available settings in test data
===================================

.. contents::
   :depth: 2
   :local:

Setting table
-------------

The Setting table is used to import test libraries, resource files and
variable files and to define metadata for test suites and test
cases. It can be included in test case files and resource files. Note
that in a resource file, a Setting table can only include settings for
importing libraries, resources, and variables.

.. table:: Settings available in the Setting table
   :class: tabular

   +-----------------+--------------------------------------------------------+
   |       Name      |                         Description                    |
   +=================+========================================================+
   | Library         | Used for `importing libraries`_.                       |
   +-----------------+--------------------------------------------------------+
   | Resource        | Used for `taking resource files into use`_.            |
   +-----------------+--------------------------------------------------------+
   | Variables       | Used for `taking variable files into use`_.            |
   +-----------------+--------------------------------------------------------+
   | Documentation   | Used for specifying a `test suite`__ or                |
   |                 | `resource file`__ documentation.                       |
   +-----------------+--------------------------------------------------------+
   | Metadata        | Used for setting `free test suite metadata`_.          |
   +-----------------+--------------------------------------------------------+
   | Suite Setup     | Used for specifying the `suite setup`_.                |
   +-----------------+--------------------------------------------------------+
   | Suite Teardown  | Used for specifying the `suite teardown`_.             |
   +-----------------+--------------------------------------------------------+
   | Force Tags      | Used for specifying forced values for tags when        |
   |                 | `tagging test cases`_.                                 |
   +-----------------+--------------------------------------------------------+
   | Default Tags    | Used for specifying default values for tags when       |
   |                 | `tagging test cases`_.                                 |
   +-----------------+--------------------------------------------------------+
   | Test Setup      | Used for specifying a default `test setup`_.           |
   +-----------------+--------------------------------------------------------+
   | Test Teardown   | Used for specifying a default `test teardown`_.        |
   +-----------------+--------------------------------------------------------+
   | Test Template   | Used for specifying a default `template keyword`_      |
   |                 | for test cases.                                        |
   +-----------------+--------------------------------------------------------+
   | Test Timeout    | Used for specifying a default `test case timeout`_.    |
   +-----------------+--------------------------------------------------------+

.. note:: All setting names can optionally include a colon at the end, for
      example :setting:`Documentation:`. This can make reading the settings easier
      especially when using the plain text format.

__ `Test suite documentation`_
__ `Documenting resource files`_

Test Case table
---------------

The settings in the Test Case table are always specific to the test
case for which they are defined. Some of these settings override the
default values defined in the Settings table.

.. table:: Settings available in the Test Case table
   :class: tabular

   +-----------------+--------------------------------------------------------+
   |      Name       |                         Description                    |
   +=================+========================================================+
   | [Documentation] | Used for specifying a `test case documentation`_.      |
   +-----------------+--------------------------------------------------------+
   | [Tags]          | Used for `tagging test cases`_.                        |
   +-----------------+--------------------------------------------------------+
   | [Setup]         | Used for specifying a `test setup`_.                   |
   +-----------------+--------------------------------------------------------+
   | [Teardown]      | Used for specifying a `test teardown`_.                |
   +-----------------+--------------------------------------------------------+
   | [Template]      | Used for specifying a `template keyword`_.             |
   +-----------------+--------------------------------------------------------+
   | [Timeout]       | Used for specifying a `test case timeout`_.            |
   +-----------------+--------------------------------------------------------+

Keyword table
-------------

Settings in the Keyword table are specific to the user keyword for
which they are defined.

.. table:: Settings available in the Keyword table
   :class: tabular

   +-----------------+--------------------------------------------------------+
   |      Name       |                         Description                    |
   +=================+========================================================+
   | [Documentation] | Used for specifying a `user keyword documentation`_.   |
   +-----------------+--------------------------------------------------------+
   | [Tags]          | Used for specifying `user keyword tags`_.              |
   +-----------------+--------------------------------------------------------+
   | [Arguments]     | Used for specifying `user keyword arguments`_.         |
   +-----------------+--------------------------------------------------------+
   | [Return]        | Used for specifying `user keyword return values`_.     |
   +-----------------+--------------------------------------------------------+
   | [Teardown]      | Used for specifying `user keyword teardown`_.          |
   +-----------------+--------------------------------------------------------+
   | [Timeout]       | Used for specifying a `user keyword timeout`_.         |
   +-----------------+--------------------------------------------------------+
