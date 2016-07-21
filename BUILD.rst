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
     git commit doc/api -m "Regenerated API docs"   # if needed

3. Repository status

   - Check that you have nothing left to commit, pull, or push::

       git status
       git pull --rebase
       git push

   - Clean up::

       invoke clean

4. Set version and GitHub login related shell variable to ease copy-pasting further commands::

     VERSION=<x.y.z>
     LOGIN=<GitHub Login>
     PASSWORD=<GitHub Password>

   GitHub login details are needed only when generating release notes.

Release notes
-------------

1. Generate a template for the release notes::

     doc/releasenotes/generate.py $VERSION $LOGIN $PASSWORD >> doc/releasenotes/rf-$VERSION.rst

2. Fill the missing details in the template.

3. Add, commit and push::

     git add doc/releasenotes/rf-$VERSION.rst
     git commit -m "Release notes for $VERSION" doc/releasenotes/rf-$VERSION.rst
     git push

4. Add short release notes to GitHub's `releases page
   <https://github.com/robotframework/robotframework/releases>`_
   with a link to the full release notes.

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

3. JAR distribution

   - Create::

       invoke jar

   - Test that JAR is not totally borken::

       java -jar dist/robotframework-$VERSION.jar --version
       java -jar dist/robotframework-$VERSION.jar atest/testdata/misc/pass_and_fail.robot

4. Upload JAR to Sonatype

   - Sonatype offers a service where users can upload JARs and they will be synced
     to the maven central repository. Below are the instructions to upload the JAR.

   - Prequisites:

      - Install maven
      - Create a `Sonatype account`__
      - Add these lines (filled with the Sonatype account information) to your ``settings.xml``::

            <servers>
                <server>
                    <id>sonatype-nexus-staging</id>
                    <username></username>
                    <password></password>
                </server>
            </servers>

      - Create `a PGP key`__
      - Apply for `publish rights`__ to org.robotframework project. This will
        take some time from them to accept.


   - Run command::

        mvn gpg:sign-and-deploy-file -Dfile=dist/robotframework-$VERSION.jar -DpomFile=pom.xml -Durl=http://oss.sonatype.org/service/local/staging/deploy/maven2/ -DrepositoryId=sonatype-nexus-staging

   - Go to https://oss.sonatype.org/index.html#welcome, log in with Sonatype credentials, find the staging repository and do close & release
   - After that, the released JAR is synced to Maven central within an hour.

__ https://issues.sonatype.org/secure/Dashboard.jspa
__ http://central.sonatype.org/pages/working-with-pgp-signatures.html
__ https://docs.sonatype.org/display/Repository/Sonatype+OSS+Maven+Repository+Usage+Guide

5. User Guide

   - Create package (updates also library docs)::

       doc/userguide/ug2html.py zip

   - Update docs at http://robotframework.org/robotframework/::

        git checkout gh-pages
        invoke add_docs $VERSION --push
        git checkout master

Announcements
-------------

- Twitter:
  http://twitter.com/robotframework
- Users and announcements mailing lists
- Robot Framework LinkedIn group:
  https://www.linkedin.com/groups/Robot-Framework-3710899
- With major releases can also consider:

  - http://opensourcetesting.org
  - http://tech.groups.yahoo.com/group/agile-testing
  - http://lists.idyll.org/listinfo/testing-in-python
  - etc.

Post-actions
------------

1. Set version back to ``dev`` if you did not do it as part of `tagging`_::

     invoke set_version --push dev

2. Close `issue tracker milestone
   <https://github.com/robotframework/robotframework/milestones>`__.

3. Update API doc version at https://readthedocs.org/projects/robot-framework/.
