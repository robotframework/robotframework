Creating Robot Framework releases
=================================

These instructions cover steps needed to create new Robot Framework releases.
Many individual steps are automated, but we do not want to automate the whole
procedure because it would be hard to react if something goes terribly wrong.
When applicable, the steps are listed as commands that can be copied and
executed on the command line.

.. contents::

Using Invoke
------------

Some tasks are automated using `Invoke <http://pyinvoke.org>`_. Generating
releases requires it to be installed::

    pip install invoke

Invoke is executed from the command line like::

    inv[oke] task [options]

Run ``invoke`` without arguments for help. All tasks can be listed using
``invoke --list`` and they are defined in `<tasks.py>`_ file.

Preparation
-----------

1. Testing

   - Check CI status at http://robot.radiaatto.ri.fi/.

   - Run acceptance tests with additional operating systems and interpreters
     if needed. See `<atest/README.rst>`_ for details.

2. Generate API docs (including JavaDocs) and see is there is something that
   should be committed::

     doc/api/generate.py
     git diff doc/api
     git commit doc/api -m "Regenerated"   # if needed

3. Repository status

   - Check that you have nothing left to commit, pull, or push::

       git status
       git pull
       git push

   - Clean up::

       invoke clean

4. Set ``$VERSION`` shell variable to ease copy-pasting further commands::

     VERSION=x.y.z

Tagging
-------

1. Tag release::

     invoke tag_release $VERSION

   This updates version information in `<src/robot/version.py>`_ and in
   `<pom.xml>`_, creates tag, and pushes changes.

2. Version back to ``dev``::

     invoke set_version --push dev

   If you are going to create distributions on the same repository, you may
   want to post-pone this step until they are done.

Creating distributions
----------------------

1. Checkout earlier created tag if necessary::

     git checkout $VERSION

2. Source distribution

   - Create and deploy::

       invoke sdist --deploy

   - Verify that https://pypi.python.org/pypi/robotframework looks good.

   - Test installation (add ``--pre`` with pre-releases)::

       pip install robotframework --upgrade

3. Windows installers

   - Create 32bit and 64bit variants on suitable machines/interpreters::

       invoke wininst

   - Manually upload to https://pypi.python.org/pypi/robotframework/.

4. JAR distribution

   - Create::

       invoke jar

   - Upload to Sonatype

     - TODO

5. User Guide

   - Create package (updates also library docs)::

       doc/userguide/ug2html.py zip

   - Update docs at http://robotframework.org/robotframework/.

     - TODO

Release notes
-------------

TODO

Announcements
-------------

TODO.

Not all places listed on the `old instructions
<https://code.google.com/p/robotframework/wiki/Releasing#Announce_Release>`_
are valid anymore.
