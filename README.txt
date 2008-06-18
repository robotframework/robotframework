Robot Framework
===============

1. Introduction
---------------

Robot Framework is a Python-based keyword-driven test automation framework with 
an easy-to-use tabular syntax for creating test cases. Its testing capabilities
can be extended by test libraries implemented either with Python or Java. 
Users can also create new keywords from existing ones using the same simple 
syntax that is used for creating test cases.

  - Enables easy-to-use tabular syntax for creating test cases in a uniform way.
  - Provides ability to create reusable higher-level keywords from the existing
    keywords.
  - Provides easy-to-read result reports and logs in HTML format.
  - Is platform and application independent.
  - Can natively use both Python and Java test code.
  - Provides a simple library API for creating customized test libraries.
  - Provides a command line interface and XML based outputs for integration into
    existing build infrastructure (continuous integration systems).
  - Provides support for Selenium for web testing, Java GUI testing, running 
    processes, Telnet, SSH, and so on.
  - Supports creating data-driven tests.
  - Provides tagging to categorize and select test cases to be executed. 

2. More Information
-------------------

Robot Framework documentation including User Guide and keyword
documentations of standard libraries can be found from 'doc'
directory. For more information e.g. about external test libraries go
to http://robotframework.org.


3. Installation
---------------

See INSTALLATION.txt for installation and uninstallation instructions.

Additionally PACKAGING.tx contains details about creating new
installation packages.


4. Directory Layout
-------------------

atest/
    Acceptance tests. Naturally using Robot Framework.

devscripts/
    Helper scripts for Robot Framework developers.

doc/
    User Guide and standard library documentation.

proto/
    Tools, scripts, etc. not yet ready for real use.

src/
    Robot Framework source code.

templates/
    Simple HTML and TSV test data templates.

tools/
    Different utilities for Robot Framework users.

utest/
    Unit tests.

