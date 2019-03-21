Continuous Integration
======================

Overview
--------

Current CI system is implemented on free tier of Azure Devops. It's currently
configured to run a combination of Linux, Windows & OSX operating systems and
different python versions.

Each test run is implemented from a single job template. Each job has
essentially 3 phases:

* Setup
* Unit Test execution
* Acceptance Test execution

Currently supports following combinations:

* OSX Python 2.7
* OSX Python 3.7
* Windows Python 2.7
* Windows Python 3.4
* Windows Python 3.5
* Windows Python 3.7
* Windows Jython 2.7
* Windows IronPython 2.7
* Linux Python 2.7
* Linux Python 3.4
* Linux Python 3.6
* Linux Python 3.7
* Linux PyPy
* Linux PyPy3


Setup
^^^^^

Depending on the OS & Python version, setup phase is only typically just
installing python specific requirements  but can also contain OS dependant tasks
like installing required native libraries or tools which are not related
directly to python.

Unit Test execution
^^^^^^^^^^^^^^^^^^^

Runs all unittests via script "utest/cirun.py". Main reason being that this
allows to collect JUnit based results file. See utest/README.rst for more
details.

Acceptance Test execution
^^^^^^^^^^^^^^^^^^^^^^^^^

Executes acceptances tests via atest/run.py. See atest/README.rst for more
details.

Azure Configuration
-------------------

Initial jobs are defined in a file "azure-pipelines.yml". First section called
"Variables" defines what python version is being used run acceptance tests as a
full path to a python interpreter already present in the build agents.

Second section defines what jobs are generated when a build is triggered. For
each job, there's a set of parameters passed to actual job template.  Here's an
example of a single job:

.. code-block::

   - template: azure/job_template.yml
     parameters:
       name: 'osx_python37'
       vmImage: 'macOS-10.13'
       extra_atest_params: ''
       timeout: 40
       os_name: 'OSX'
       python_type: 'Python'
       python_version: 3.7
       python_binary: '/Users/vsts/hostedtoolcache/Python/3.7.0/x64/python'
       runner_binary: $(osx_runner)

Explanation:


* Template - defines what template file is used for the job. Currently all
  jobs are defined in a single template file and tasks within said job are
  conditionally executed depending on other parameters.
* Name - Name of the job that is shown in the build log.
* vmImage - base image name used by the job when it gets executed.
* extra_atest_params - extra string that can be passed into acceptance test
  execution. For example, one could pass --include or --exclude flags here.
* timeout - how long the specific job can run before it is cancelled.
* os_name - Platform Identifier. Currently used values: "Windows", "Linux",
  "OSX". This value is used to install os specific dependencies but also as
  identifier string when locating acceptance results directory which includes
  OS name in the directory.
* Python_type - Python type identifier. Its used to identify what sort of
  dependencies should be installed but also as identifier string when
  locating acceptance results directory which includes python type in the
  directory.
  Currently used values: "Python", "Jython", "PyPy", "IronPython".
  See "Installing Python Dependencies" for more details.
* Python_version - major python version. Currently only used as identifier
  string when locating acceptance results directory which includes version
  in the directory.
* Python_binary - full path under which all the tests are executed.
* Runner_binary - full path to python which executes the acceptance tests that
  will then take care of triggering the tests under python_binary.

Installing Python Dependencies
------------------------------

Python dependencies for CI environment use different set of requirements.txt
files as normal development or release workflow. Partly this is because certain
python versions and their pip implementations do not share same functionality.

Each "Python Type" has its own root level requirements file, for example if
python_type is set to "Python", setup phase will run following command:

.. code-block::

   pip install -r requirements-ci-Python.txt

That file then install all the dependencies defined in that file, and then move
on to read plain "requirements-ci.txt" which ones again moves to read
"requirements-build.txt".

Structure for defining ci time dependencies should be following:


* requirements-ci.txt

  * all common dependencies that *do not require* any annotations.

* requirements-ci-${python_type}

  * everything else. Can contain annotations if the platform/pip supports
    them.

Results
-------

When logged into Azure Devops console, on the left side menu should contain entry
"Pipelines". After selecting it, "Builds" should be available. If there are
multiple projects, all of them are shown but select Robot Framework and you
should see a history of all the builds then on the right side.

When you select a single job, you are presented with a 3 tabs: "Logs", "Summary"
& "Tests".

Logs
^^^^

Lists all the jobs for this particular cycle. Selecting what ever one, allows
you to dig into console output of each step.

Summary
^^^^^^^

Shows a aggrated status of the jobs. Main interest here is the link to build
artifacts. Each job archives its own robot test logs into its own zip file which
can be then downloaded from here.

Tests
^^^^^

Shows the information gathered from JUnit logs for acceptance & unit tests.
Here you can see what went wrong and what the console looked like when the test
failed.
