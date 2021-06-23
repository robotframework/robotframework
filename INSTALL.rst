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
<http://python.org>`_ and supports also `Jython <http://jython.org>`_ (JVM),
`IronPython <http://ironpython.net>`_ (.NET) and `PyPy <http://pypy.org>`_.
Before installing the framework, an obvious precondition_ is installing at
least one of these interpreters.

Different ways to install Robot Framework itself are listed below and explained
more thoroughly in the subsequent sections.

`Installing with pip`_
    Using pip_ is the recommended way to install Robot Framework. As the
    standard Python package manager it is included in the latest Python,
    Jython and IronPython versions. If you already have pip available, you
    can simply execute::

        pip install robotframework

`Installing from source`_
    This approach works regardless the operating system and the Python
    interpreter used. You can get the source code either by downloading a
    source distribution from `PyPI <https://pypi.python.org/pypi/robotframework>`_
    and extracting it, or by cloning the
    `GitHub repository <https://github.com/robotframework/robotframework>`_ .

`Standalone JAR distribution`_
    If running tests with Jython is enough, the easiest approach is downloading
    the standalone ``robotframework-<version>.jar`` from `Maven central
    <http://search.maven.org/#search%7Cga%7C1%7Ca%3Arobotframework>`_.
    The JAR distribution contains both Jython and Robot Framework and thus
    only requires having `Java <http://java.com>`_ installed.

`Manual installation`_
    If you have special needs and nothing else works, you can always do
    a custom manual installation.

.. note:: Prior to Robot Framework 3.0, there were also separate Windows
          installers for 32bit and 64bit Python versions. Because Python 2.7.9 and
          newer contain pip_ on Windows and Python 3 would have needed two
          more installers, it was decided that `Windows installers are not
          created anymore`__. The recommend installation approach also on
          Windows is `using pip`_.

__ https://github.com/robotframework/robotframework/issues/2218

Preconditions
-------------

Robot Framework is supported on Python_ (both Python 2 and Python 3), Jython_
(JVM) and IronPython_ (.NET) and PyPy_. The interpreter you want to use should
be installed before installing the framework itself.

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

Python 2 vs Python 3
~~~~~~~~~~~~~~~~~~~~

Python 2 and Python 3 are mostly the same language, but they are not fully
compatible with each others. The main difference is that in Python 3 all
strings are Unicode while in Python 2 strings are bytes by default, but there
are also several other backwards incompatible changes.

Python 2 itself has `not been officially supported since 2020`__, but Robot
Framework still supports it mainly to support Jython_ and IronPython_ that
do not have Python 3 compatible releases available. Python 2 support will,
however, be removed in `Robot Framework 5.0`__.

All users are recommended to upgrade to Python 3. For Jython and IronPython
users this unfortunately means that they need some new way to run Robot
Framework on their environment. For IronPython users the pythonnet__ module
is typically a good alternative, but for Jython users there is no such simple
solution available.

__ https://www.python.org/doc/sunset-python-2/
__ https://github.com/robotframework/robotframework/issues/3457
__ http://pythonnet.github.io/

Python installation
~~~~~~~~~~~~~~~~~~~

On most UNIX-like systems such as Linux and OS X you have Python_ installed
by default. If you are on Windows or otherwise need to install Python yourself,
a good place to start is http://python.org. There you can download a suitable
installer and get more information about the installation process and Python
in general.

Robot Framework 4.x versions still support Python 2.7 and Python 3.5 and newer,
but the `plan is to drop Python 2 and 3.5 support soon`__.

After installing Python, you probably still want to configure PATH_ to make
Python itself as well as the ``robot`` and ``rebot`` `runner scripts`_
executable on the command line.

.. tip:: Latest Python Windows installers allow setting ``PATH`` as part of
         the installation. This is disabled by default, but `Add Python 3.x
         to PATH` can be enabled as `explained here`__.

__ https://github.com/robotframework/robotframework/issues/3457
__ https://docs.python.org/3/using/windows.html#the-full-installer

Jython installation
~~~~~~~~~~~~~~~~~~~

Using test libraries implemented with Java_ or that use Java tools internally
requires running Robot Framework on Jython_, which in turn requires Java
Runtime Environment (JRE) or Java Development Kit (JDK). Installing either
of these Java distributions is out of the scope of these instructions, but
you can find more information, for example, from http://java.com.

Installing Jython is a fairly easy procedure, and the first step is getting
an installer from http://jython.org. The installer is an executable JAR
package, which you can run from the command line like `java -jar
jython_installer-<version>.jar`. Depending on the  system configuration,
it may also be possible to just double-click the installer.

Robot Framework 3.0 supports Jython 2.7 which requires Java 7 or newer.
If older Jython or Java versions are needed, Robot Framework 2.5-2.8 support
Jython 2.5 (requires Java 5 or newer) and Robot Framework 2.0-2.1 support
Jython 2.2.

After installing Jython, you probably still want to configure PATH_ to make
Jython itself as well as the ``robot`` and ``rebot`` `runner scripts`_
executable on the command line.

IronPython installation
~~~~~~~~~~~~~~~~~~~~~~~

IronPython_ allows running Robot Framework on the `.NET platform
<http://www.microsoft.com/net>`__ and interacting with C# and other .NET
languages and APIs. Only IronPython 2.7 is supported in general and
IronPython 2.7.9 or newer is highly recommended.

If not using IronPython 2.7.9 or newer and Robot Framework 3.1 or newer,
an additional requirement is installing
`ElementTree <http://effbot.org/downloads/#elementtree>`__
module 1.2.7 preview release. This is required because the ElementTree
module distributed with older IronPython versions was broken. Once you
have `pip activated for IronPython`__, you can easily install ElementTree
using this command:

.. sourcecode:: bash

    ipy -m pip install http://effbot.org/media/downloads/elementtree-1.2.7-20070827-preview.zip

Alternatively you can download the zip package, extract it, and install it by
running ``ipy setup.py install`` on the command prompt in the created directory.

After installing IronPython, you probably still want to configure PATH_ to make
IronPython itself as well as the ``robot`` and ``rebot`` `runner scripts`_
executable on the command line.

__ `Installing pip for IronPython`_

PyPy installation
~~~~~~~~~~~~~~~~~

PyPy_ is an alternative implementation of the Python language with both Python 2
and Python 3 compatible versions available. Its main advantage over the
standard Python implementation is that it can be faster and use less memory,
but this depends on the context where and how it is used. If execution speed
is important, at least testing PyPY is probably a good idea.

Installing PyPy is a straightforward procedure and you can find both installers
and installation instructions at http://pypy.org. After installation you
probably still want to configure PATH_ to make PyPy itself as well as the
``robot`` and ``rebot`` `runner scripts`_ executable on the command line.

Configuring ``PATH``
~~~~~~~~~~~~~~~~~~~~

The ``PATH`` environment variable lists locations where commands executed in
a system are searched from. To make using Robot Framework easier from the
command prompt, it is recommended to add the locations where the `runner
scripts`_ are installed into the ``PATH``. It is also often useful to have
the interpreter itself in the ``PATH`` to make executing it easy.

When using Python on UNIX-like machines both Python itself and scripts
installed with should be automatically in the ``PATH`` and no extra actions
needed. On Windows and with other interpreters the ``PATH`` must be configured
separately.

.. tip:: Latest Python Windows installers allow setting ``PATH`` as part of
         the installation. This is disabled by default, but `Add Python 3.x
         to PATH` can be enabled as `explained here`__. Enabling it will add
         both the Python installation directory and the :file:`Scripts`
         directory to the ``PATH``.

__ https://docs.python.org/3/using/windows.html#the-full-installer

What directories to add to ``PATH``
'''''''''''''''''''''''''''''''''''

What directories you need to add to the ``PATH`` depends on the interpreter and
the operating system. The first location is the installation directory of
the interpreter (e.g. :file:`C:\\Python27`) and the other is the location
where scripts are installed with that interpreter. Both Python and IronPython
install scripts to :file:`Scripts` directory under the installation directory
on Windows (e.g. :file:`C:\\Python27\\Scripts`) and Jython uses :file:`bin`
directory regardless the operating system (e.g. :file:`C:\\jython2.7.0\\bin`).

Notice that the :file:`Scripts` and :file:`bin` directories may not be created
as part of the interpreter installation, but only later when Robot Framework
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
``robot`` or ``rebot`` `runner script`_ will always use the one that is
*first* in the ``PATH`` regardless under what Python version that script is
installed. To avoid that, you can always execute the `installed robot module
directly`__ like `C:\Python27\python.exe -m robot`.

Notice also that you should not add quotes around directories you add into
the ``PATH`` (e.g. `"C:\Python27\Scripts"`). Quotes `can cause problems with
Python programs <http://bugs.python.org/issue17023>`_ and they are not needed
in this context even if the directory path would contain spaces.

__ `Executing installed robot module`_

Setting ``PATH`` on UNIX-like systems
'''''''''''''''''''''''''''''''''''''

On UNIX-like systems you typically need to edit either some system wide or user
specific configuration file. Which file to edit and how depends on the system,
and you need to consult your operating system documentation for more details.

Setting ``https_proxy``
~~~~~~~~~~~~~~~~~~~~~~~

If you are `installing with pip`_ and are behind a proxy, you need to set
the ``https_proxy`` environment variable. It is needed both when installing
pip itself and when using it to install Robot Framework and other Python
packages.

How to set the ``https_proxy`` depends on the operating system similarly as
`configuring PATH`_. The value of this variable must be an URL of the proxy,
for example, `http://10.0.0.42:8080`.

Installing with pip
-------------------

The standard Python package manager is pip_, but there are also other
alternatives such as `Buildout <http://buildout.org>`__ and `easy_install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`__. These instructions
only cover using pip, but other package managers ought be able to install
Robot Framework as well.

Latest Python, Jython, IronPython and PyPy versions contain pip bundled in.
Which versions contain it and how to possibly activate it is discussed in
sections below. See pip_ project pages if for the latest installation
instructions if you need to install it.

.. note:: Robot Framework 3.1 and newer are distributed as `wheels
          <http://pythonwheels.com>`_, but earlier versions are available only
          as source distributions in tar.gz format. It is possible to install
          both using pip, but installing wheels is a lot faster.

Installing pip for Python
~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from Python 2.7.9, the standard Windows installer by default installs
and activates pip. Assuming you also have configured PATH_ and possibly
set https_proxy_, you can run `pip install robotframework` right after
Python installation. With Python 3.4 and newer pip is officially part of the
interpreter and should be automatically available.

Outside Windows and with older Python versions you need to install pip yourself.
You may be able to do it using system package managers like Apt or Yum on Linux,
but you can always use the manual installation instructions found from the pip_
project pages.

If you have multiple Python versions with pip installed, the version that is
used when the ``pip`` command is executed depends on which pip is first in the
PATH_. An alternative is executing the ``pip`` module using the selected Python
version directly:

.. sourcecode:: bash

    python -m pip install robotframework
    python3 -m pip install robotframework

Installing pip for Jython
~~~~~~~~~~~~~~~~~~~~~~~~~

Jython 2.7 contain pip bundled in, but it needs to be activated before using it
by running the following command:

.. sourcecode:: bash

    jython -m ensurepip

Jython installs its pip into :file:`<JythonInstallation>/bin` directory.
Does running `pip install robotframework` actually use it or possibly some
other pip version depends on which pip is first in the PATH_. An alternative
is executing the ``pip`` module using Jython directly:

.. sourcecode:: bash

    jython -m pip install robotframework

Installing pip for IronPython
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IronPython 2.7.5 and newer contain pip bundled in. With IronPython 2.7.9 and
newer pip also works out-of-the-box, but with earlier versions it needs to be
activated with `ipy -m ensurepip` similarly as with Jython.

With IronPython 2.7.7 and earlier you need to use `-X:Frames` command line
option when activating pip like `ipy -X:Frames -m ensurepip` and also
when using it. Prior to IronPython 2.7.9 there were problems creating
possible start-up scripts when installing modules. Using IronPython 2.7.9
is highly recommended.

IronPython installs pip into :file:`<IronPythonInstallation>/Scripts` directory.
Does running `pip install robotframework` actually use it or possibly some
other pip version depends on which pip is first in the PATH_. An alternative
is executing the ``pip`` module using IronPython directly:

.. sourcecode:: bash

    ipy -m pip install robotframework

Installing pip for PyPy
~~~~~~~~~~~~~~~~~~~~~~~

Also PyPy contains pip bundled in. It is not activated by default, but it can
be activated similarly as with the other interpreters:

.. sourcecode:: bash

    pypy -m ensurepip
    pypy3 -m ensurepip

If you have multiple Python versions with pip installed, the version that is
used when the ``pip`` command is executed depends on which pip is first in the
PATH_. An alternative is executing the ``pip`` module using PyPy directly:

.. sourcecode:: bash

    pypy -m pip
    pypy3 -m pip

Using pip
~~~~~~~~~

Once you have pip_ installed, and have set https_proxy_ if you are behind
a proxy, using pip on the command line is very easy. The easiest way to use
pip is by letting it find and download packages it installs from the
`Python Package Index (PyPI)`__, but it can also install packages
downloaded from the PyPI separately. The most common usages are shown below
and pip_ documentation has more information and examples.

__ PyPI_

.. sourcecode:: bash

    # Install the latest version (does not upgrade)
    pip install robotframework

    # Upgrade to the latest version
    pip install --upgrade robotframework

    # Install a specific version
    pip install robotframework==4.0.3

    # Install separately downloaded package (no network connection needed)
    pip install robotframework-4.0.3.tar.gz

    # Install latest (possibly unreleased) code directly from GitHub
    pip install https://github.com/robotframework/robotframework/archive/master.zip

    # Uninstall
    pip uninstall robotframework

Notice that pip installs only stable releases by default.
If you want to install an alpha, beta or release candidate, you need to either
specify the version explicitly or use the :option:`--pre` option:

.. sourcecode:: bash

    # Install 4.0 beta 1
    pip install robotframework==4.0b1

    # Upgrade to the latest version even if it is a pre-release
    pip install --pre --upgrade robotframework

Installing from source
----------------------

This installation method can be used on any operating system with any of the
supported interpreters. Installing *from source* can sound a bit scary, but
the procedure is actually pretty straightforward.

Getting source code
~~~~~~~~~~~~~~~~~~~

You typically get the source code by downloading a *source distribution* from
PyPI_. Starting from Robot Framework 3.1 the source distribution is a zip
package and with earlier versions it is in tar.gz format. Once you have
downloaded the package, you need to extract it somewhere and, as a result,
you get a directory named `robotframework-<version>`. The directory contains
the source code and a ``setup.py`` script needed for installing it.

An alternative approach for getting the source code is cloning project's
`GitHub repository`_ directly. By default you will get the latest code, but
you can easily switch to different released versions or other tags.

Installation
~~~~~~~~~~~~

Robot Framework is installed from source using Python's standard ``setup.py``
script. The script is in the directory containing the sources and you can run
it from the command line using any of the supported interpreters:

.. sourcecode:: bash

   python setup.py install
   jython setup.py install
   ipy setup.py install
   pypy setup.py install

The ``setup.py`` script accepts several arguments allowing, for example,
installation into a non-default location that does not require administrative
rights. It is also used for creating different distribution packages. Run
`python setup.py --help` for more details.

Standalone JAR distribution
---------------------------

Robot Framework is also distributed as a standalone Java archive that contains
both Jython_ and Robot Framework and only requires Java_ a dependency. It is
an easy way to get everything in one package that  requires no installation,
but has a downside that it does not work with the normal Python_ interpreter.

The package is named ``robotframework-<version>.jar`` and it is available
on the `Maven central`_. After downloading the package, you can execute tests
with it like:

.. sourcecode:: bash

  java -jar robotframework-4.0.3.jar mytests.robot
  java -jar robotframework-4.0.3.jar --variable name:value mytests.robot

If you want to `post-process outputs`_ using Rebot or use other built-in
`supporting tools`_, you need to give the command name ``rebot``, ``libdoc``,
``testdoc`` or ``tidy`` as the first argument to the JAR file:

.. sourcecode:: bash

  java -jar robotframework-4.0.3.jar rebot output.xml
  java -jar robotframework-4.0.3.jar libdoc MyLibrary list

For more information about the different commands, execute the JAR without
arguments.

In addition to the Python standard library and Robot Framework modules, the
standalone JAR version contains the PyYAML dependency needed to handle YAML
variable files.

Manual installation
-------------------

If you do not want to use any automatic way of installing Robot Framework,
you can always install it manually following these steps:

1. Get the source code. All the code is in a directory (a package in Python)
   called :file:`robot`. If you have a `source distribution`_ or a version
   control checkout, you can find it from the :file:`src` directory, but you
   can also get it from an earlier installation.

2. Copy the source code where you want to.

3. Decide `how to run tests`__.

__ `Executing Robot Framework`_

Verifying installation
----------------------

After a successful installation, you should be able to execute the created
`runner scripts`_ with :option:`--version` option and get both Robot Framework
and interpreter versions as a result:

.. sourcecode:: bash

   $ robot --version
   Robot Framework 4.0.3 (Python 3.8.5 on linux)

   $ rebot --version
   Rebot 4.0.3 (Python 3.8.5 on linux)

If running these commands fails with a message saying that the command is
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
with Jython and IronPython, the scripts are typically either in :file:`Scripts`
or :file:`bin` directory under the interpreter installation directory.

Uninstallation
--------------

The easiest way to uninstall Robot Framework is using pip_:

.. sourcecode:: bash

   pip uninstall robotframework

A nice feature in pip is that it can uninstall packages even if they are
installed from the source. If you do not have pip available or have done
a `manual installation`_ to a custom location, you need to find `where files
are installed`_ and remove them manually.

If you have set PATH_ or configured the environment otherwise, you need to
undo those changes separately.

Upgrading
---------

If you are using pip_, upgrading to a new version requires either specifying
the version explicitly or using the :option:`--upgrade` option. If upgrading
to a preview release, :option:`--pre` option is needed as well.

.. sourcecode:: bash

   # Upgrade to the latest stable version. This is the most common method.
   pip install --upgrade robotframework

   # Upgrade to the latest version even if it would be a preview release.
   pip install --upgrade --pre robotframework

   # Upgrade to the specified version.
   pip install robotframework==4.0.3

When using pip, it automatically uninstalls previous versions before
installation. If you are `installing from source`_, it should be safe to
just install over an existing installation. If you encounter problems,
uninstallation_ before installation may help.

When upgrading Robot Framework, there is always a change that the new version
contains backwards incompatible changes affecting existing tests or test
infrastructure. Such changes are very rare in minor versions like 3.2.2 or
4.0.3, but more common in major versions like 3.2 and 4.0. Backwards
incompatible changes and deprecated features are explained in the release
notes, and it is a good idea to study them especially when upgrading to
a new major version.

Executing Robot Framework
-------------------------

Using ``robot`` and ``rebot`` commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework tests are executed using the ``robot`` command and results
post-processed with the ``rebot`` command:

.. sourcecode:: bash

    robot tests.robot
    rebot output.xml

Both of these commands are installed as part of the normal installation and
can be executed directly from the command line if PATH_ is set correctly.

Executing installed ``robot`` module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An alternative way to run tests is executing the installed ``robot`` module
or its sub module ``robot.run`` directly using Python's `-m command line
option`__. This is especially useful if Robot Framework is used with multiple
Python versions:

.. sourcecode:: bash

    python -m robot tests.robot
    python3 -m robot.run tests.robot
    jython -m robot tests.robot
    /opt/jython/jython -m robot tests.robot

Post-processing outputs using the same approach works too, but the module to
execute is ``robot.rebot``:

.. sourcecode:: bash

    python -m robot.rebot output.xml

__ https://docs.python.org/using/cmdline.html#cmdoption-m

Executing installed ``robot`` directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you know where Robot Framework is installed, you can also execute the
installed :file:`robot` directory or the :file:`run.py` file inside it
directly:

.. sourcecode:: bash

   python path/to/robot/ tests.robot
   jython path/to/robot/run.py tests.robot

Post-processing outputs using the :file:`robot/rebot.py` file works the same
way too:

.. sourcecode:: bash

   python path/to/robot/rebot.py output.xml

Executing Robot Framework this way is especially handy if you have done
a `manual installation`_.

Using virtual environments
--------------------------

Python `virtual environments`__ allow Python packages to be installed in
an isolated location for a particular system or application, rather than
installing all packages into the same global location. Virtual environments
can be created using the virtualenv__ tool or, starting from Python 3.3,
using the standard venv__ module.

__ https://packaging.python.org/installing/#creating-virtual-environments
__ https://virtualenv.pypa.io
__ https://docs.python.org/3/library/venv.html

.. These aliases need an explicit target to work in GitHub
.. _precondition: `Preconditions`_
.. _PATH: `Configuring PATH`_
.. _https_proxy: `Setting https_proxy`_
.. _source distribution: `Getting source code`_
.. _runner script: `Using robot and rebot commands`_
.. _runner scripts: `Using robot and rebot commands`_
