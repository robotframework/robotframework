class InternalLinking:
    """Library for testing libdoc's internal linking.

    Custom links are (case-insensitively):
    - `Introduction`
    - `Library INTROduction`
    - `importing`
    - `Library Importing`

    Also linking to keywords works:
    - `Keyword`
    - `secoNd kEywoRD`

    Non-matching `backticks` just get special formatting.
    """

    def __init__(self, argument=None):
        """Importing section. See `introduction` and `keyword` for details."""

    def keyword(self):
        """First keyword here. See also `Importing` and `Second Keyword`."""

    def second_keyword(self, arg):
        """We got `arg`. And have `no link`."""
