Installation instructions
=========================

These instructions cover installing and uninstalling Robot Framework and its
preconditions on different operating systems. If you already have `pip
<http://pip-installer.org>`_ installed, it is enough to run::

    pip install robotframework

.. contents::
   :depth: 2
   :local:

.. START USER GUIDE IGNORE
.. These instructions are included also in the User Guide. Following role
.. and link definitions are excluded when UG is built.
.. default-role:: code
.. role:: file(emphasis)
.. role:: option(code)
.. _supporting tools: http://robotframework.org/robotframework/#built-in-tools
.. _post-process outputs: `supporting tools`_
.. END USER GUIDE IGNORE

Introduction
------------

`Robot Framework <http://robotframework.org>`_ is implemented with `Python
<http://python.org>`_ and also runs on `Jython <http://jython.org>`_ (JVM) and
`IronPython <http://ironpython.net>`_ (.NET). Before installing the framework,
an obvious precondition_ is installing at least one of these interpreters. Note
that Python 3 is not yet supported, but there is an `un-official Python 3 port
<https://pypi.python.org/pypi/robotframework-python3>`_ available.

Different ways to install Robot Framework itself are listed below and explained
more thoroughly in subsequent sections.

`Package managers (e.g. pip)`_
    Python package managers make installation trivial. For example, pip_ users
    just need to execute::

        pip install robotframework

    As the standard Python package manager, pip is bundled in with the latest
    Python, Jython and IronPython installers.

`Installing from source`_
    This approach works regardless the operating system and the Python
    interpreter used. You can get the source code either by downloading and
    extracting a source distribution from `PyPI
    <https://pypi.python.org/pypi/robotframework>`_ or by cloning the
    `GitHub repository <https://github.com/robotframework/robotframework>`_ .

`Using Windows installer`_
    There are graphical installers for both 32 bit and 64 bit Windows systems,
    both available on PyPI_.

`Standalone JAR distribution`_
    If running tests with Jython is enough, the easiest approach is downloading
    the standalone ``robotframework-<version>.jar`` from `Maven central
    <http://search.maven.org/#search%7Cga%7C1%7Ca%3Arobotframework>`_.
    The JAR distribution contains both Jython and Robot Framework and thus
    only requires having `Java <http://java.com>`_ installed.

`Manual installation`_
    If you have special needs and nothing else works, you can always do
    a custom manual installation.

Preconditions
-------------

Robot Framework is supported on Python_, Jython_ (JVM) and IronPython_ (.NET)
and runs also on `PyPy <http://pypy.org>`_. The interpreter you want to use
should be installed before installing the framework.

Which interpreter to use depends on the needed test libraries and test
environment in general. Some libraries use tools or modules that only work
with Python, while others may use Java tools that require Jython or need
.NET and thus IronPython. There are also many tools and libraries that run
fine with all interpreters.

If you do not have special needs or just want to try out the framework,
it is recommended to use Python. It is the most mature implementation,
considerably faster than Jython or IronPython (especially start-up time is
faster), and also readily available on most UNIX-like operating systems.
Another good alternative is using the `standalone JAR distribution`_ that
only has Java as a precondition.

Python installation
~~~~~~~~~~~~~~~~~~~

On most UNIX-like systems such as Linux and OS X you have Python_ installed
by default. If you are on Windows or otherwise need to install Python yourself,
a good place to start is http://python.org. There you can download a suitable
installer and get more information about the installation process and Python
in general.

Robot Framework 2.8 and older support Python 2.5, 2.6, and 2.7, but
Robot Framework 2.9 will drop Python 2.5 support. The plan is to support
also Python 3 in the future, latest with Robot Framework 3.0. If you need
Python 3 support earlier, you can use the `un-official Python 3 port`_. If
you need to use really old Python versions, Robot Framework 2.0 and 2.1
support Python 2.3 and 2.4.

On Windows it is recommended to install Python to all users and to run the
installer as an administrator. Additionally, environment variable
``PYTHONCASEOK`` must not be set.

After installing Python, you probably still want to `configure PATH`_ to make
the ``pybot`` `runner script`_ executable on the command prompt.

.. tip:: Latest Python Windows installers allow setting ``PATH`` as part of
         the installation. This is disabled by default, but `Add python.exe
         to Path` can be enabled on the `Customize Python` screen.

Jython installation
~~~~~~~~~~~~~~~~~~~

Using test libraries implemented with Java_ or that use Java tools internally
requires running Robot Framework on Jython_, which in turn requires Java
Runtime Environment (JRE) or Java Development Kit (JDK). Installing either
of these Java implementations is out of the scope of these instructions, but
you can find more information from http://java.com if needed.

Installing Jython is a fairly easy procedure, and the first step is getting
an installer from http://jython.org. The installer is an executable JAR
package, which you can run from the command line like `java -jar
jython_installer-<version>.jar`. Depending on the  system configuration,
it may also be possible to just double-click the installer.

Robot Framework 2.8 and older support Jython 2.5 (requires Java 5 or newer)
and Jython 2.7 (requires Java 7 or newer). The forthcoming Robot Framework
2.9 will require Jython 2.7. If ancient Jython versions are needed, Robot
Framework 2.0 and 2.1 support Jython 2.2.

After installing Jython, you probably still want to `configure PATH`_ to make
the ``jybot`` `runner script`_ executable on the command prompt.

IronPython installation
~~~~~~~~~~~~~~~~~~~~~~~

IronPython_ allows running Robot Framework on the `.NET platform
<http://www.microsoft.com/net>`__ and interacting with C# and other .NET
languages and APIs. Only IronPython 2.7 is supported.

When using IronPython, an additional dependency is installing
`elementtree <http://effbot.org/downloads/#elementtree>`__
module 1.2.7 preview release. This is required because the ``elementtree``
module distributed with IronPython is
`broken <http://ironpython.codeplex.com/workitem/31923>`__. You can install
the package by downloading the source distribution, unzipping it, and running
`ipy setup.py install` on the command prompt in the created directory.

After installing IronPython, you probably still want to `configure PATH`_ to
make the ``ipybot`` `runner script`_ executable on the command prompt.

Configuring ``PATH``
~~~~~~~~~~~~~~~~~~~~

The ``PATH`` environment variable lists locations where commands executed in
a system are searched from. To make using Robot Framework easier from the
command prompt, it is recommended to add the locations where the `runner
scripts`_ are installed into the ``PATH``. The runner scripts themselves
require the matching interpreter to be in the ``PATH`` and thus the
interpreter installation directory must be added there too.

When using Python on UNIX-like machines both Python itself and scripts
installed with should be automatically in the ``PATH`` and no extra actions
needed. On Windows and with other interpreters the ``PATH`` must be configured
separately.

.. tip:: Latest Python Windows installers allow setting ``PATH`` as part of
         the installation. This is disabled by default, but `Add python.exe
         to Path` can be enabled on the `Customize Python` screen. It will
         set both Python installation directory and :file:`Scripts` directory
         to ``PATH``.

What directories to add to ``PATH``
'''''''''''''''''''''''''''''''''''

What directories you need to add to the ``PATH`` depends on the interpreter and
the operating system. The first location is the installation directory of
the interpreter (e.g. :file:`C:\\Python27`) and the other is the location
where scripts are installed with that interpreter. Both Python and IronPython
install scripts to :file:`Scripts` directory under the installation directory
on Windows (e.g. :file:`C:\\Python27\\Scripts`) and Jython uses :file:`bin`
directory regardless the operating system (e.g. :file:`C:\\jython2.5.3\\bin`).

Notice that :file:`Scripts` and :file:`bin` directories may not be created
as part of the interpreter installation but only later when Robot Framework
or some other third party module is installed.

Setting ``PATH`` on Windows
'''''''''''''''''''''''''''

On Windows you can configure ``PATH`` by following the steps below. Notice
that the exact setting names may be different on different Windows versions,
but the basic approach should still be the same.

1. Open `Control Panel > System > Advanced > Environment Variables`. There
   are `User variables` and `System variables`, and the difference between
   them is that user variables affect only the current users, whereas system
   variables affect all users.

2. To edit an existing ``PATH`` value, select `Edit` and add
   `;<InstallationDir>;<ScriptsDir>` at the end of the value (e.g.
   `;C:\Python27;C:\Python27\Scripts`). Note that the semicolons (`;`) are
   important as they separate the different entries. To add a new ``PATH``
   value, select `New` and set both the name and the value, this time without
   the leading semicolon.

3. Exit the dialog with `Ok` to save the changes.

4. Start a new command prompt for the changes to take effect.

Notice that if you have multiple Python versions installed, the executed
``pybot`` script will always use the one that is *first* in the ``PATH``
regardless under what Python version that script is installed. To avoid that,
you can always use the `direct entry points`_ with the interpreter of choice
like `C:\Python26\python.exe -m robot.run`.

Notice also that you should not add quotes around directories you add into
the ``PATH`` (e.g. `"C:\Python27\Scripts"`). Quotes `can cause problems with
Python programs <http://bugs.python.org/issue17023>`_ and they are not needed
with the ``PATH`` even if the directory path would contain spaces.


Setting ``PATH`` on UNIX-like systems
'''''''''''''''''''''''''''''''''''''

On UNIX-like systems you typically need to edit either some system wide or user
specific configuration file. Which file to edit and how depends on the system,
and you need to consult your operating system documentation for more details.

Setting ``https_proxy``
~~~~~~~~~~~~~~~~~~~~~~~

If you are planning to `use pip for installation`_ and are behind a proxy, you
need to set the ``https_proxy`` environment variable. It is needed both when
installing pip and when using it to install Robot Framework and other Python
packages.

How to set the ``https_proxy`` depends on the operating system similarly as
`configuring PATH`_. The value of this variable must be an URL of the proxy,
for example, `http://10.0.0.42:8080`.

Installing Robot Framework
--------------------------

Package managers (e.g. pip)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The standard Python package manager is pip_, but there are also other
alternatives such as `Buildout <http://buildout.org>`__ and `easy_install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`__. These instructions
only cover using pip, but other package managers ought be able to install
Robot Framework as well, at least if they search packages from PyPI_.

Latest Python, Jython and IronPython versions contain pip bundled in. Which
versions contain it and how to possibly activate it is discussed in sections
below. If you need to install pip separately, latest installation instructions
can be found from pip_ project pages.

.. note:: If you are behind a proxy, you need to `set https_proxy`_ environment
          variable before installing and using pip.

          Only Robot Framework 2.7 and newer can be installed using pip. If you
          need an older version, you must use other installation approaches.

Installing pip for Python
'''''''''''''''''''''''''

Starting from Python 2.7.9, the standard Windows installer by default installs
and activates pip. Assuming you also have `configured PATH`__ and possibly
`set https_proxy`_, you can run `pip install robotframework` right after
Python installation.

Outside Windows and with older Python versions you need to install pip yourself.
You may be able to do it using system package managers like `apt` on Linux, but
you can always use manual installation instructions found from pip_ project
pages.

.. tip:: You can also run pip like `python -m pip install robotframework`. This
         is especially useful if you have pip installed also for other Python
         interpreters.

__ `Configuring PATH`_

Installing pip for Jython
'''''''''''''''''''''''''

Latest preview releases of the forthcoming Jython 2.7 contain pip bundled in.
It just needs to be activated by running the following command before using it::

    jython -m ensurepip

Jython installs its own version of pip into `<JythonInstallation>/bin`
directory. Does executing `pip` actually run it or possibly some other pip
version depends on how ``PATH`` is configured. It can thus be safer to use
`jython -m pip install robotframework` instead.

Older Jython versions do not officially support pip.

Installing pip for IronPython
'''''''''''''''''''''''''''''

IronPython contains bundled pip starting from `version 2.7.5`__. Similarly as
with Jython, it needs to be activated first::

    ipy -X:Frames -m ensurepip

Notice that with IronPython `-X:Frames` command line option is needed both
when activating and using pip.

IronPython installs its own version of pip into `<IronPythonInstallation>/Scripts`
directory. Does executing `pip` actually run it or possibly some other pip
version depends on how ``PATH`` is configured. It can thus be safer to use
`ipy -X:Frames -m pip install robotframework` instead.

Older IronPython versions do not officially support pip.

__ http://blog.ironpython.net/2014/12/pip-in-ironpython-275.html

Using pip
'''''''''

Once you have pip installed, using it on the command line is very easy. The
most common usages are shown below and pip_ documentation has more information
and examples.

.. sourcecode:: bash

    # Install the latest version
    pip install robotframework

    # Upgrade to the latest version
    pip install --upgrade robotframework

    # Install a specific version
    pip install robotframework==2.8.5

    # Uninstall
    pip uninstall robotframework

Notice that pip 1.4 and newer will only install stable releases by default.
If you want to install an alpha, beta or release candidate, you need to either
specify the version explicitly or use :option:`--pre` option:

.. sourcecode:: bash

    # Install 2.9 beta 1
    pip install robotframework==2.9b1

    # Install the latest version even if it is a pre-release
    pip install --pre robotframework

If you still use pip 1.3 or older and do not want to get the latest version
when it is a pre-release, you need to explicitly specify which stable version
you want to install.

Installing from source
~~~~~~~~~~~~~~~~~~~~~~

This installation method can be used on any operating system with any of the
supported interpreters. Installing *from source* can sound a bit scary, but
the procedure is actually pretty straightforward.

.. _source distribution:

Getting source code
'''''''''''''''''''

You typically get the source by downloading a *source distribution package*
in `.tar.gz` format. Newer packages are available on PyPI_, but Robot Framework
2.8.1 and older can be found from the old `Google Code download page
<https://code.google.com/p/robotframework/downloads/list?can=1>`_.
Once you have downloaded the package, you need to extract it somewhere and,
as a result, you get a directory named `robotframework-<version>`. The
directory contains the source code and scripts needed for installing it.

An alternative approach for getting the source code is cloning project's
`GitHub repository`_ directly. By default you will get the latest code, but
you can easily switch to different released versions or other tags.

Installation
''''''''''''

Robot Framework is installed from source using Python's standard ``setup.py``
script. The script is in the directory containing the sources and you can run
it from the command line using any of the supported interpreters:

.. sourcecode:: bash

   # Installing with Python. Creates `pybot` and `rebot` scripts.
   python setup.py install

   # Installing with Jython. Creates `jybot` and `jyrebot` scripts.
   jython setup.py install

   # Installing with IronPython. Creates `ipybot` and `ipyrebot` scripts.
   ipy setup.py install

The ``setup.py`` script accepts several arguments allowing, for example,
installation into a non-default location that does not require administrative
rights. It is also used for creating different distribution packages. Run
`python setup.py --help` for more details.

Using Windows installer
~~~~~~~~~~~~~~~~~~~~~~~

There are separate graphical installers for 32 bit and 64 bit Windows systems
with names in format ``robotframework-<version>.win32.exe`` and
``robotframework-<version>.win-amd64.exe``, respectively. Newer installers
are on PyPI_ and Robot Framework 2.8.1 and older on the old `Google Code
download page`_. Running the installer requires double-clicking it and
following the simple instructions.

Windows installers always run on Python and create the standard ``pybot`` and
``rebot`` `runner scripts`_. Unlike the other provided installers, these
installers also automatically create ``jybot`` and ``ipybot`` scripts. To be
able to use the created runner scripts, both the :file:`Scripts` directory
containing them and the appropriate interpreters need to be in PATH_.

Installing Robot Framework may require administrator privileges. In that case
select `Run as administrator` from the context menu when starting the
installer.

Standalone JAR distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework is also distributed as a standalone Java archive that contains
both Jython_ and Robot Framework and only requires Java_ a dependency. It is
an easy way to get everything in one package that  requires no installation,
but has a downside that it does not work with the normal Python_ interpreter.

The package is named ``robotframework-<version>.jar`` and it is available
on the `Maven central`_. After downloading the package, you can execute tests
with it like:

.. sourcecode:: bash

  java -jar robotframework-2.8.5.jar mytests.txt
  java -jar robotframework-2.8.5.jar --variable name:value mytests.txt

If you want to `post-process outputs`_ using Rebot or use other built-in
`supporting tools`_, you need to give the command name ``rebot``, ``libdoc``,
``testdoc`` or ``tidy`` as the first argument to the JAR file:

.. sourcecode:: bash

  java -jar robotframework-2.8.5.jar rebot output.xml
  java -jar robotframework-2.8.5.jar libdoc MyLibrary list

For more information about the different commands, execute the JAR without
arguments.

Manual installation
~~~~~~~~~~~~~~~~~~~

If you do not want to use any automatic way of installing Robot Framework,
you can always install it manually following these steps:

1. Get the source code. All the code is in a directory (a package in Python)
   called :file:`robot`. If you have a `source distribution`_ or a version
   control checkout, you can find it from the :file:`src` directory, but you
   can also get it from an earlier installation.

2. Copy the source code where you want to.

3. Create `runner scripts`_ you need or use the `direct entry points`_
   with the interpreter of your choice.

Verifying installation
~~~~~~~~~~~~~~~~~~~~~~

After a successful installation, you should be able to execute created `runner
scripts`_ with :option:`--version` option and get both Robot Framework and
interpreter versions as a result:

.. sourcecode:: bash

   $ pybot --version
   Robot Framework 2.8.5 (Python 2.7.3 on linux2)

   $ rebot --version
   Rebot 2.8.5 (Python 2.7.3 on linux2)

   $ jybot --version
   Robot Framework 2.8.5 (Jython 2.5.3 on java1.7.0_60)

If running the runner scripts fails with a message saying that the command is
not found or recognized, a good first step is double-checking the PATH_
configuration. If that does not help, it is a good idea to re-read relevant
sections from these instructions before searching help from the Internet or
as asking help on `robotframework-users
<http://groups.google.com/group/robotframework-users/>`__ mailing list or
elsewhere.

Where files are installed
~~~~~~~~~~~~~~~~~~~~~~~~~

When an automatic installer is used, Robot Framework source code is copied
into a directory containing external Python modules. On UNIX-like operating
systems where Python is pre-installed the location of this directory varies.
If you have installed the interpreter yourself, it is normally
:file:`Lib/site-packages` under the interpreter installation directory, for
example, :file:`C:\\Python27\\Lib\\site-packages`. The actual Robot
Framework code is in a directory named :file:`robot`.

Robot Framework `runner scripts`_ are created and copied into another
platform-specific location. When using Python on UNIX-like systems, they
normally go to :file:`/usr/bin` or :file:`/usr/local/bin`. On Windows and
with other interpreters, the scripts are typically either in :file:`Scripts`
or :file:`bin` directory under the interpreter installation directory.

Uninstallation and upgrading
----------------------------

Uninstallation
~~~~~~~~~~~~~~

How to uninstall Robot Framework depends on the original installation method.
Notice that if you have set ``PATH`` or configured your environment otherwise,
you need to undo these changes separately.

Uninstallation using pip
''''''''''''''''''''''''

If you have pip available, uninstallation is as easy as installation:

.. sourcecode:: bash

   pip uninstall robotframework

A nice pip feature is that it can uninstall packages even if installation has
been done using some other approach.

Uninstallation after using Windows installer
''''''''''''''''''''''''''''''''''''''''''''

If `Windows installer`_  has been used, uninstallation can be done using
`Control Panel > Add/Remove Programs`. Robot Framework is listed under
Python applications.

Manual uninstallation
'''''''''''''''''''''

The framework can always be uninstalled manually. This requires removing the
created :file:`robot` directory and the `runner scripts`_. See `where files
are installed`_ section above to learn where they can be found.

Upgrading
~~~~~~~~~

When upgrading or downgrading Robot Framework, it is safe to install a new
version over the existing when switching between two minor versions, for
example, from 2.8.4 to 2.8.5. This typically works also when upgrading to
a new major version, for example, from 2.8.5 to 2.9, but uninstalling the old
version is always safer.

A very nice feature of pip package manager is that it automatically
uninstalls old versions when upgrading. This happens both when changing to
a specific version or when upgrading to the latest version:

.. sourcecode:: bash

   pip install robotframework==2.7.1
   pip install --upgrade robotframework

Regardless on the version and installation method, you do not need to
reinstall preconditions or set ``PATH`` environment variable again.

Different entry points
----------------------

Runner scripts
~~~~~~~~~~~~~~

Robot Framework has different runner scripts for executing test cases and for
post-processing outputs based on earlier test results. In addition to that,
these scripts are different depending on the interpreter that is used:

.. table:: Different runner scripts
   :class: tabular

   =============  ==============  ================
    Interpreter   Test execution  Post-processing
   =============  ==============  ================
   Python         ``pybot``       ``rebot``
   Jython         ``jybot``       ``jyrebot``
   IronPython     ``ipybot``      ``ipyrebot``
   =============  ==============  ================

On UNIX-like operating systems such as Linux and OS X, the runner scripts
are implemented using Python, and on Windows they are batch files. Regardless
of the operating system, using any of these scripts requires that the
appropriate interpreter is in PATH_.

Direct entry points
~~~~~~~~~~~~~~~~~~~

In addition to the above runner scripts, it is possible to both run tests and
post-process outputs by executing framework's entry points directly using a
selected interpreter. It is possible to execute them as modules using Python's
:option:`-m` option and, if you know where the framework is installed, to run
them as scripts. The entry points are listed on the following table using
Python, and examples below illustrate using them also with other interpreters.

.. table:: Direct entry points
   :class: tabular

   ==================  =======================  ============================
       Entry point          Run as module              Run as script
   ==================  =======================  ============================
   Test execution      `python -m robot.run`    `python path/robot/run.py`
   Post-processing     `python -m robot.rebot`  `python path/robot/rebot.py`
   ==================  =======================  ============================

.. sourcecode:: bash

   # Run tests with Python by executing `robot.run` module.
   python -m robot.run

   # Run tests with Jython by running `robot/run.py` script.
   jython path/to/robot/run.py

   # Create reports/logs with IronPython by executing `robot.rebot` module.
   ipy -m robot.rebot

   # Create reports/logs with Python by running `robot/rebot.py` script.
   python path/to/robot/rebot.py


.. _runner script: `runner scripts`_
.. _precondition: preconditions_
.. _configure PATH: `Configuring PATH`_
.. _PATH: `Configuring PATH`_
.. _use pip for installation: `Package managers (e.g. pip)`_
.. _set https_proxy: `Setting https_proxy`_
.. _Windows installer: `Using Windows installer`_
.. _entry point: `direct entry points`_
