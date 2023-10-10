Available settings
==================

This appendix lists all settings that can be used in different sections.

.. note:: Settings can be localized_. See the Translations_ appendix for
          supported translations.

.. contents::
   :depth: 2
   :local:

Setting section
---------------

The Setting section is used to import libraries, resource files and
variable files and to define metadata for test suites and test
cases. It can be included in test case files and resource files. Note
that in a resource file, a Setting section can only include settings for
importing libraries, resources, and variables.

.. table:: Settings available in the Setting section
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
   | Name            | Used for setting a custom `suite name`_.               |
   +-----------------+--------------------------------------------------------+
   | Documentation   | Used for specifying a `suite`__ or                     |
   |                 | `resource file`__ documentation.                       |
   +-----------------+--------------------------------------------------------+
   | Metadata        | Used for setting `free suite metadata`_.               |
   +-----------------+--------------------------------------------------------+
   | Suite Setup     | Used for specifying the `suite setup`_.                |
   +-----------------+--------------------------------------------------------+
   | Suite Teardown  | Used for specifying the `suite teardown`_.             |
   +-----------------+--------------------------------------------------------+
   | Test  Tags      | Used for specifying `test case tags`_ for all tests    |
   |                 | in a suite.                                            |
   +-----------------+--------------------------------------------------------+
   | Force Tags,     | `Deprecated settings`__ for specifying test case tags. |
   | Default Tags    |                                                        |
   +-----------------+--------------------------------------------------------+
   | Keyword Tags    | Used for specifying `user keyword tags`_ for all       |
   |                 | keywords in a certain file.                            |
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
   | Task Setup,     | Aliases for Test Setup, Test Teardown, Test Template   |
   | Task Teardown,  | and Test Timeout, respectively, that can be used when  |
   | Task Template,  | `creating tasks`_.                                     |
   | Task Timeout    |                                                        |
   +-----------------+--------------------------------------------------------+

__ `Suite documentation`_
__ `Documenting resource files`_
__ `Deprecation of Force Tags and Default Tags`_

Test Case section
-----------------

The settings in the Test Case section are always specific to the test
case for which they are defined. Some of these settings override the
default values defined in the Settings section.

Exactly same settings are available when `creating tasks`_ in the Task section.

.. table:: Settings available in the Test Case section
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

Keyword section
---------------

Settings in the Keyword section are specific to the user keyword for
which they are defined.

.. table:: Settings available in the Keyword section
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
   | [Setup]         | Used for specifying a `user keyword setup`_.           |
   |                 | New in Robot Framework 7.0.                            |
   +-----------------+--------------------------------------------------------+
   | [Teardown]      | Used for specifying `user keyword teardown`_.          |
   +-----------------+--------------------------------------------------------+
   | [Timeout]       | Used for specifying a `user keyword timeout`_.         |
   +-----------------+--------------------------------------------------------+
   | [Return]        | Used for specifying `user keyword return values`_.     |
   |                 | Deprecated in Robot Framework 7.0. Use the RETURN_     |
   |                 | statement instead.                                     |
   +-----------------+--------------------------------------------------------+
