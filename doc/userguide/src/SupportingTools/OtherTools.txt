Other tools distributed with Robot Framework
--------------------------------------------

The tools listed below are included with Robot Framework project,
but unlike the built-in tools libdoc_, testdoc_, and tidy_, they need to
be installed separately. The tool name links to a wiki page that contains
both the tool documentation and the tool itself for download.

risto.py__
    Generating graphs about historical statistics of test executions.

fixml.py__
    A tool for fixing broken `output files`_.

times2csv.py__
    Generating start, end and elapsed time information about suites, tests
    and keywords in CSV format

statuschecker.py__
    Tool for verifying that test case statuses and messages and also keyword
    log messages are as expected

robotdiff.py__
    Tool for showing differences between different test runs based on
    `output files`_.

fileviewer.py_
    Graphical tool implementing UNIX :prog:`tail` like functionality.
    Especially designed to view `debug files`_.

`One Click Installer`_
    A tool for installing Robot Framework and its preconditions on Windows XP
    machines.

__ http://code.google.com/p/robotframework/wiki/HistoricalReportingTool
__ http://code.google.com/p/robotframework/wiki/OutputFileFixingTool
__ http://code.google.com/p/robotframework/wiki/ExecutionTimeReportingTool
__ http://code.google.com/p/robotframework/wiki/TestStatusCheckerTool
__ http://code.google.com/p/robotframework/wiki/TestResultDiffingTool
.. _fileviewer.py: http://code.google.com/p/robotframework/wiki/FileViewingTool
.. _One Click Installer: http://code.google.com/p/robotframework/wiki/OneClickInstaller

External tools
--------------

External tools are developed as separate projects. Some of the more mature
tools are listed below, but because new tools are introduced pretty often
the list is not exhaustive. To get your tool listed here, please contact the
developers using the `mailing lists`_.

RIDE_
    RIDE is a standalone tool for editing test data. It helps in
    creating, editing and maintaining of Robot Framework test data.

mabot_
    Standalone tool for reporting manual test execution results. It enables
    storing and reporting manual test cases along with automated Robot
    Framework test cases.

JavalibCore_
    Provides a collection base classes helpful in creation of larger Java
    test libraries by offering several dynamic ways of resolving available
    keywords at runtime

RemoteApplications__
    A proxy test library that enables testing applications running on different
    JVM as Robot Framework, including Java Webstart applications.

`Jenkins plugin`__
    A plugin for Jenkins__, a popular continuous integration server, for
    collecting and publishing Robot Framework test results.

`Maven plugin`__
    Robot Framework plugin for Maven__ build tool.

`Ant plugin`__
    Robot Framework plugin for Ant__ build tool.

`robot-mode`__
    Emacs__ mode for Robot Framework.

`robotframework-vim`__
    Vim__ plugins for development with Robot framework

`Robot.tmbundle`__
    TextMate__ bundle for Robot Framework.

.. _RIDE: https://github.com/robotframework/RIDE
.. _mabot: http://code.google.com/p/robotframework-mabot
.. _JavalibCore: https://github.com/robotframework/JavalibCore
__ https://github.com/robotframework/RemoteApplications
__ https://wiki.jenkins-ci.org/display/JENKINS/Robot+Framework+Plugin
__ http://jenkins-ci.org/
__ http://code.google.com/p/robotframework-maven-plugin/
__ http://maven.apache.org/
__ http://code.google.com/p/robotframework-ant/
__ http://ant.apache.org/
__ https://github.com/sakari/robot-mode
__ http://www.gnu.org/software/emacs/
__ https://github.com/mfukar/robotframework-vim
__ http://www.vim.org/
__ https://bitbucket.org/jussimalinen/robot.tmbundle/wiki/Home
__ http://macromates.com/
