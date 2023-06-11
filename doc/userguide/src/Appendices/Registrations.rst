Registrations
=============

This appendix lists file extensions, media types, and so on, that are
associated with Robot Framework.

Suite file extensions
---------------------

`Suite files`_ with the following extensions are parsed automatically:

:file:`.robot`
    Suite file using the `plain text format`_.

:file:`.robot.rst`
    Suite file using the `reStructuredText format`_.

:file:`.rbt`
    Suite file using the `JSON format`_.

Using other extensions is possible, but it requires `separate configuration`__.

__ `Selecting files to parse`_

Resource file extensions
------------------------

`Resource files`_ can use the following extensions:

:file:`.resource`
    Recommended when using the plain text format.

:file:`.robot`, :file:`.txt` and :file:`.tsv`
    Supported with the plain text format for backwards compatibility reasons.
    :file:`.resource` is recommended and may be mandated in the future.

:file:`.rst` and :file:`.rest`
    Resource file using the `reStructuredText format`__.

:file:`.rsrc` and :file:`.json`
    Resource file using the `JSON format`__.

__ `Resource files using reStructured text format`_
__ `Resource files using JSON format`_

Media type
----------

The media type to use with Robot Framework data is `text/robotframework`.

Remote server port
------------------

The default `remote server`__ port is 8270. The port has been `registered by IANA`__.

__ `Remote library interface`_
__ https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml?search=8270
