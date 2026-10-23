"""Library with shared reStructuredText references.

Examples
========

.. _project: https://example.com/robot
.. _keyword-alias: `My Keyword`_

See `My Keyword`_ and project_.
"""

ROBOT_LIBRARY_DOC_FORMAT = "REST"


def my_keyword(name="Robot", count=1):
    """Run the example.

    See examples_ and project_ and introduction_.

    Example::

        My Keyword    Robot    2
        Log    ${name}

    :param str name: The **user** name.
    :param count: Number of repetitions.
    :type count: int
    :custom: This field is preserved.
    """


def local_reference():
    """Local definitions take precedence over library references.

    project_

    See keyword-alias_ as well.

    .. _project: https://example.com/local
    """
