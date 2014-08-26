Installation instructions
=========================

These instructions cover installing and uninstalling Robot Framework and its
preconditions on different operating systems.

.. contents::
   :depth: 2
   :local:

Introduction
------------

.. tip:: If you have pip_ installed, just run :cli:`pip install robotframework`.

Supported installation approaches
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework is implemented with Python_ and also runs on Jython_ (JVM) and
IronPython_ (.NET). Before installing the framework, an obvious precondition_
is installing at least one of these interpreters. Notice that Python 3.x
versions are not yet supported, but there is an `un-official Python 3 port
<https://pypi.python.org/pypi/robotframework-python3>`__ available.

Different ways to install Robot Framework itself are listed below and explained
more thoroughly in subsequent sections.

`Using Python package managers`_
    Python package managers such as pip_ make installation trivial. Using them
    adds a precondition to install the package manager itself first, though.

`Installing from source`_
    This approach works regardless the operating system and the Python
    interpreter used. You can get the source code either by downloading
    and extracting a source distribution from PyPI_ or by cloning the
    GitHub_ repository.

`Using Windows installer`_
    There are graphical installers for both 32 bit and 64 bit Windows systems,
    both available on PyPI_.

`Standalone jar distribution`_
    If running tests with Jython is enough, the easiest approach is downloading
    the standalone :prog:`robotframework-<version>.jar` from `Maven central`_.
    The jar distribution contains both Jython and Robot Framework

`Manual installation`_
    If you have special needs and nothing else works, you can always do
    a custom manual installation.

.. _Python: http://python.org
.. _Jython: http://jython.org
.. _IronPython: http://ironpython.net
.. _PyPy: http://pypy.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _Maven central: http://search.maven.org/#search%7Cga%7C1%7Ca%3Arobotframework
.. _GitHub: https://github.com/robotframework/robotframework

Different entry points
~~~~~~~~~~~~~~~~~~~~~~

.. _runner script:

Runner scripts
''''''''''''''

Robot Framework has different entry points for executing test cases and for
post-processing outputs based on earlier test results. For both of
these usages there are also different runner scripts for different
interpreters:

.. table:: Different runner scripts
   :class: tabular

   =============  ==============  ================
    Interpreter   Test execution  Post-processing
   =============  ==============  ================
   Python         :prog:`pybot`   :prog:`rebot`
   Jython         :prog:`jybot`   :prog:`jyrebot`
   IronPython     :prog:`ipybot`  :prog:`ipyrebot`
   =============  ==============  ================

On UNIX-like operating systems such as Linux and OSX, the runner scripts
are implemented using Python, and on Windows they are batch files. Regardless
of the operating system, using any of these scripts requires that the
appropriate interpreter is in PATH_.

.. _entry point:
.. _direct entry points:

Running tests and post-processing output directly
'''''''''''''''''''''''''''''''''''''''''''''''''

In addition to the above runner scripts, it is possible to both
run tests and post-process outputs by executing framework's entry points
directly using a selected interpreter. It is possible to execute
them as modules using Python's :opt:`-m` option and, if you know where
the framework is installed, to run them as scripts. The entry points
are listed on the following table using Python, and examples below
illustrate using them also with other interpreters.

.. table:: Direct entry points
   :class: tabular

   ==================  ============================  ==================================
       Entry point              Run as module                   Run as script
   ==================  ============================  ==================================
   Test execution      :cli:`python -m robot.run`    :cli:`python path/robot/run.py`
   Post-processing     :cli:`python -m robot.rebot`  :cli:`python path/robot/rebot.py`
   ==================  ============================  ==================================

.. sourcecode:: bash

   # Run tests with Python by executing `robot.run` module.
   python -m robot.run

   # Run tests with Jython by running `robot/run.py` script.
   jython path/to/robot/run.py

   # Create reports/logs with IronPython by executing `robot.rebot` module.
   ipy -m robot.rebot

   # Create reports/logs with Python by running `robot/rebot.py` script.
   python path/to/robot/rebot.py

.. _precondition:

Preconditions
-------------

Robot Framework is supported on Python_, Jython_ (JVM) and IronPython_ (.NET)
and should also run on PyPy_. The interpreter you want to use should be
installed before installing the framework.

Which interpreter to use depends on the needed test libraries and test
environment in general. Some libraries use tools or modules that only work
with Python, while others may use Java tools that require Jython or need
.NET and thus IronPython. There are also many tools and libraries that run
fine with all interpreters.

If you you do not have special needs or just want to try out the framework,
it is recommended to use Python. It is the most mature implementation,
considerably faster than Jython or IronPython (especially start-up time is
faster), and also readily available on most UNIX-like operating systems.
Another good alternative is using the `standalone jar distribution`_ that
only has Java as a precondition.

Python installation
~~~~~~~~~~~~~~~~~~~

On most UNIX-like systems such as Linux and OS X, you have Python_
installed by default. If you are on Windows or otherwise need to
install Python yourself, a good best place to start is http://python.org.
There you can download a suitable installer and get more information about
the installation process and Python in general.

Robot Framework currently supports Python versions 2.5, 2.6 and 2.7. The plan
is to support also Python 3 versions in the future and to drop Python 2.5
support. Robot Framework 2.5 and earlier support Python versions 2.3-2.4.

.. note::  Running Robot Framework on Python using :prog:`pybot` `runner
           script`_ requires :prog:`python` to be executable on the command
           prompt. This means that you need to make sure it is in PATH_.

.. note::  On Windows it is recommended to install Python to all users
           and to run the installation as an administrator.

.. note::  Environment variable :var:`PYTHONCASEOK` should be not set on Windows
           machines. Robot Framework will not work correctly with it.

Jython installation
~~~~~~~~~~~~~~~~~~~

Using test libraries implemented with Java or using Java tools internally
requires running Robot Framework on Jython_, which in turn requires Java
Runtime Environment (JRE). Installing Jython is a fairly easy procedure,
and the first step is getting an installer from http://jython.org. The
installer is an executable jar package, which you can run from the command
line like :cli:`java -jar jython_installer-<version>.jar`. Depending on the
system configuration, it may also be possible to just double-click the
installer.

Starting from Robot Framework 2.5, the minimum supported Jython version is 2.5
which requires Java 5 (a.k.a. Java 1.5) or newer. Earlier Robot Framework
versions support also Jython 2.2.

.. note::  Running Robot Framework on Jython using :prog:`jybot` `runner
           script`_ requires :prog:`jython` to be executable on the command
           prompt. This means that you need to make sure it is in PATH_.

IronPython installation
~~~~~~~~~~~~~~~~~~~~~~~

IronPython_ allows running Robot Framework on the .NET platform. Only
IronPython 2.7 is supported.

When using IronPython, an additional dependency is installing
`elementtree <http://effbot.org/downloads/#elementtree>`_
module 1.2.7 preview release. This is required because the :code:`elementtree`
module distributed with IronPython is
`broken <http://ironpython.codeplex.com/workitem/31923>`_. You can install
the package by downloading the source distribution, unzipping it, and running
:cli:`ipy setup.py install` on the command prompt in the created directory.

.. note::  Running Robot Framework on IronPython using :prog:`ipybot` `runner
           script`_ requires :prog:`ipy` to be executable on the command prompt.
           This means that you need to make sure it is in PATH_.

.. _PATH:

Setting :var:`PATH`
~~~~~~~~~~~~~~~~~~~

To be able to use Robot Framework, you need to make sure :var:`PATH` environment
variable is configured correctly.

The :var:`PATH` environment variable lists locations where commands
executed in a system are searched from. To make using Robot Framework
easier from the command prompt, it is recommended to add the locations
where the `runner scripts`_ are installed into :var:`PATH`. The runner
scripts themselves require the matching interpreter to be in :var:`PATH`,
so the installation location must be added there too.

When using Python on UNIX-like machines both Python itself and scripts
installed with should be automatically in :var:`PATH` and no extra actions
needed. On Windows and with other interpreters :var:`PATH` must be configured
separately.

What directories to add to :var:`PATH`
''''''''''''''''''''''''''''''''''''''

What directories you need to add to :var:`PATH` depends on the
interpreter and operating system. The first location is the installation
directory of the interpreter (e.g. :path:`C:\\Python27`) and the other is
the location where scripts are installed with that interpreter. Both Python
and IronPython install scripts to :path:`Scripts` directory under the
installation directory on Windows (e.g. :path:`C:\\Python27\\Scripts`)
but Jython uses :path:`bin` directory (e.g. :path:`C:\\jython2.5.2\\bin`).

.. note::  On Windows it is highly recommended to add at least Python
           installation directory into :var:`PATH` *before* installing
           Robot Framework itself.

.. note::  :path:`Scripts` and :path:`bin` directories may not be created
           as part of the interpreter installation but only later when
           Robot Framework or some other third party module is installed.

Setting :var:`PATH` on Windows
''''''''''''''''''''''''''''''

On Windows you can configure :var:`PATH` by following the steps
below. Notice that the exact setting names may be different on
different Windows versions, but the basic approach should still be the same.

  1. Open :gui:`Start > Settings > Control Panel > System > Advanced >
     Environment Variables`.  There are :gui:`User variables` and
     :gui:`System variables`, and the difference between them is that user
     variables affect only the current users, whereas system variables
     affect all users.

  2. To edit the existing :var:`PATH`, select :gui:`Edit` and add
     :code:`;<InstallationDir>;<ScriptsDir>` at the end of the value
     (e.g. :code:`;C:\\Python27;C:\\Python27\\Scripts`).
     Note that the semicolons (:code:`;`) are important as they separate
     the different entries. To add a new value, select :gui:`New` and set both
     the name and the value, this time without the leading semicolon.

  3. Exit the dialog with :gui:`Ok` to save the changes.

  4. Start a new command prompt for the changes to take effect.

.. note:: Do not add quotes around directories you add into :var:`PATH`
          (e.g. :code:`"C:\\Python27\\Scripts"`). Quotes `can cause problems
          with Python programs <http://bugs.python.org/issue17023>`_
          and they are not needed with :var:`PATH` on Windows even if
          the directory path contains spaces.

Setting :var:`PATH` on UNIX-like systems
''''''''''''''''''''''''''''''''''''''''

On UNIX-like systems you typically need to edit either some system
wide or user specific configuration file. Which file to edit and how
depends on the system, and you need to consult your operating system
documentation for more details.

Setting :var:`https_proxy`
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you plan to `use pip for installation <Using Python package managers_>`_
and are behind a proxy, you also need to set :var:`https_proxy` environment
variable. It is needed both when installing pip and when using it to install
Robot Framework and other Python packages.

How to set :var:`https_proxy` depends on the operating system similarly as
setting PATH_. The value of this variable must be an URL of the proxy, for
example, :code:`http://10.0.0.42`.

Installing Robot Framework
--------------------------

Using Python package managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most popular Python package manager is pip_, but there are also other
alternatives such as
`easy_install <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ and
`Buildout <http://buildout.org>`_. These instructions only cover using pip,
but other package managers ought be able to install Robot Framework as well.

Installing pip
''''''''''''''

The hardest part of using pip is installing the tool itself, but luckily
nowadays also that is pretty simple. You can find the latest installation
instructions from `pip project pages <pip_>`_. Just remember that if you
are behind a proxy, you need to `set https_proxy environment variable
<Setting https_proxy_>`_ before installing and using pip.

A bigger problem is that at the time of this writing only Python supports
pip. The forthcoming Jython 2.7 ought to support it and even have it bundled
in, though, but it is unclear if/when IronPython will support it.

Using pip
'''''''''

Once you have pip installed, using it is very easy:

.. sourcecode:: bash

    # Install the latest version
    pip install robotframework

    # Upgrade to the latest version
    pip install --upgrade robotframework

    # Install a specific version
    pip install robotframework==2.8.5

    # Uninstall
    pip uninstall robotframework

Notice that pip and also easy_install have a "feature" that unless a specific
version is given, they install the latest possible version even if it is
an alpha or beta release. For example, if 2.8.5 is the latest stable version
and there is also 2.9 beta release available, running
:cli:`pip install robotframework` will install the latter. A workaround
is giving the version explicitly like :cli:`pip install robotframework==2.8.5`.

Installing from source
~~~~~~~~~~~~~~~~~~~~~~

This installation method can be used on any operating system with any
of the supported interpreters. Installing *from source* can sound a
bit scary, but the procedure is actually pretty straightforward.

.. _source distribution:

Getting source code
'''''''''''''''''''

You typically get the source by downloading a *source distribution package*
in :code:`.tar.gz` format from PyPI_. You need to extract
the package somewhere and, as a result, you get a directory named
:code:`robotframework-<version>`. The directory contains the source code and
scripts needed for installing it.

An alternative approach for getting the source code is cloning project's
`GitHub repository <GitHub_>`__
directly. By default you will get the latest code, but you can easily switch
to different released versions or other tags.

Installation
''''''''''''

Robot Framework is installed from source using Python's standard
:prog:`setup.py` script. The script is on the directory containing the sources
and you can run it from the command line using any of the supported
interpreters:

.. sourcecode:: bash

   # Installing with Python. Creates `pybot` and `rebot` scripts.
   python setup.py install

   # Installing with Jython. Creates `jybot` and `jyrebot` scripts.
   jython setup.py install

   # Installing with IronPython. Creates `ipybot` and `ipyrebot` scripts.
   ipy setup.py install

The :prog:`setup.py` script accepts several arguments allowing,
for example, installation into non-default locations that do not require
administrative rights. It is also used for creating different distribution
packages. Run :cli:`python setup.py --help` for more details.

.. _Windows installer:

Using Windows installer
~~~~~~~~~~~~~~~~~~~~~~~

There are separate graphical installers for 32 bit and 64 bit Windows
systems. The former installer has name in format
:prog:`robotframework-<version>.win32.exe` and the latter
:prog:`robotframework-<version>.win-amd64.exe`, and both are available on
PyPI_. Running the installer requires double-clicking it and
following the simple instructions.

Windows installers always run on Python and create the standard :prog:`pybot`
and :prog:`rebot` `runner scripts`_. Unlike the other provided installers,
these installers also automatically create :prog:`jybot` and :prog:`ipybot`
scripts. To be able to use the created runner scripts, both the
:path:`Scripts` directory containing them and the appropriate interpreters
need to be in PATH_.

.. note::  It is highly recommended to set Python installation directory into
           :var:`PATH` *before* running Robot Framework installer.

.. note::  If you have multiple versions of Python or other interpreters
           installed, the executed runner scripts will always use the one
           that is *first* in :var:`PATH` regardless under what Python version
           that script is installed. To avoid that, you can always use
           the `direct entry points`_ with the interpreter of choice like
           :cli:`C:\\Python26\\python.exe -m robot.run`.

.. note::  Installing Robot Framework may require administrator privileges.
           In that case select :gui:`Run as administrator` from the context menu
           when starting the installer.

Standalone jar distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework is also distributed as a standalone Java archive that
contains both Jython and Robot Framework and only requires Java 5 or newer
as a dependency. It is an easy way to get everything in one package that
requires no installation, but has a downside that it does not work with Python.

The package is named :prog:`robotframework-<version>.jar` and it is available
on the `Maven central`_. After downloading the package, you can execute tests
with it like:

.. sourcecode:: bash

  java -jar robotframework-2.8.5.jar mytests.txt
  java -jar robotframework-2.8.5.jar --variable name:value mytests.txt

If you want to `post-process outputs`_ or use the built-in `supporting tools`_,
you need to give the command name :prog:`rebot`, :prog:`libdoc`, :prog:`testdoc`
or :prog:`tidy` as the first argument to the JAR file:

.. sourcecode:: bash

  java -jar robotframework-2.8.5.jar rebot output.xml
  java -jar robotframework-2.8.5.jar libdoc MyLibrary list

For more information about the different commands, execute the JAR file without
arguments.

Manual installation
~~~~~~~~~~~~~~~~~~~

If you do not want to use any automatic way of installing Robot Framework,
you can always do it manually following these steps:

1. Get the source code. All the code is in a directory (a package in
   Python) called :path:`robot`. If you have a `source distribution`_ or
   a version control checkout, you can find it from the :path:`src`
   directory, but you can also get it from an earlier installation.

2. Copy the source code where you want to.

3. Create `runner scripts`_ you need or use the `direct entry points`_
   with the interpreter of your choice.

Verifying installation
~~~~~~~~~~~~~~~~~~~~~~

After a successful installation, you should be able to execute created `runner
scripts`_ with :opt:`--version` option and get both Robot Framework and
interpreter versions as a result.

.. sourcecode:: bash

   $ pybot --version
   Robot Framework 2.8.5 (Python 2.7.3 on linux2)

   $ rebot --version
   Rebot 2.8.5 (Python 2.7.3 on linux2)

   $ jybot --version
   Robot Framework 2.8.5 (Jython 2.5.2 on java1.6.0_21)

Where files are installed
~~~~~~~~~~~~~~~~~~~~~~~~~

When an automatic installer is used, the Robot Framework code is copied
into a directory containing external Python modules. On UNIX-like operating
systems where Python is pre-installed the location of this directory varies.
If you have installed the interpreter yourself, it is normally
:path:`Lib/site-packages` under the interpreter installation directory, for
example, :path:`C:\\Python27\\Lib\\site-packages`. The actual Robot
Framework code is in a directory named :path:`robot`.

Robot Framework `runner scripts`_ are created and copied into another
platform-specific location. When using Python on UNIX-like systems, they
normally go to :path:`/usr/bin` or :path:`/usr/local/bin`. On Windows and
with other interpreters, the scripts are typically either in :path:`Scripts`
or :path:`bin` directory under the interpreter installation directory.

Uninstallation and upgrading
----------------------------

Uninstallation
~~~~~~~~~~~~~~

How to uninstall Robot Framework depends on the original installation method.
Notice that if you have set :var:`PATH` or configured your environment
otherwise, you need to undo these changes separately.

Uninstallation using pip
''''''''''''''''''''''''

If you have pip available, uninstallation is as easy as installation:

.. sourcecode:: bash

   pip uninstall robotframework

A nice feature is that pip can uninstall packages even if installation has
been done using some other approach.

Uninstallation after using Windows installer
''''''''''''''''''''''''''''''''''''''''''''

If `Windows installer`_  has been used, uninstallation can be done using
:gui:`Control Panel > Add/Remove Programs`. Robot Framework is listed under
Python applications.

Manual uninstallation
'''''''''''''''''''''

The framework can always be uninstalled manually. This requires removing
:code:`robot` module as well as the created `runner scripts`_ from locations
`where files are installed`_.

Upgrading
~~~~~~~~~

When upgrading or downgrading Robot Framework, it is safe to install a new
version over the existing when switching between two minor versions,
for example, from 2.8.4 to 2.8.5. This typically works also when upgrading to
a new major version, for example, from 2.8.5 to 2.9, but uninstalling the old
version is always safer.

A very nice feature of pip package manager is that it automatically
uninstalls old versions when upgrading. This happens both when changing to
a specific version or when upgrading to the latest version:

.. sourcecode:: bash

   pip install robotframework==2.7.1
   pip install --upgrade robotframework

Regardless on the version and installation method, you do not need to
reinstall preconditions or set :var:`PATH` environment variable again.
