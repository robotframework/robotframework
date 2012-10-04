class InternalLinking:
    """Library for testing libdoc's internal linking.

    = Linking to sections =

    - `Introduction`
    - `Library INTROduction`
    - `importing`
    - `Library Importing`
    - `ShortCuts`
    - `Keywords`

    = Linking to keywords =

    - `Keyword`
    - `secoNd kEywoRD`

    = Linking to headers =

    == First level header can be linked ==

    - `linking to headers`
    - `first = level =`

    == Other levels cannot be linked ==

    - `Second level`
    - `Third level`

    =   First = Level = =

    == Second level ==

    === Third level ===

    = Formatting =

    Non-matching `backticks` just get special formatting.
    """

    def __init__(self, argument=None):
        """Importing. See `introduction`, `formatting` and `keyword` for details."""

    def keyword(self):
        """First keyword here. See also `Importing` and `Second Keyword`."""

    def second_keyword(self, arg):
        """We got `arg`. And have `no link`. Even on `second level`.

        = Not linkable =

        We are `linking to headers` and `shortcuts` but not to `not linkable`.
        """
