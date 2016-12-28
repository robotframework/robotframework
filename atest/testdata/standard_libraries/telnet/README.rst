Telnet library tests
====================

To run the Telnet library acceptance tests you will need to have a telnet
server running at localhost and accepting login from user ``test`` with password
``test``. Needless to say, you probably don't want this server to be visible to
public internet.

The user ``test`` is also assumed to have home directory at ``/home/test`` and
prompt set at ``PS1='\u@\h \W \$ '``. These are defaults at least on Debian
based systems.

Telnet library has an optional dependency to ``pyte`` module to support
terminal emulation. It is needed to make all tests pass and can be installed
with the familiar ``pip install pyte`` command.
