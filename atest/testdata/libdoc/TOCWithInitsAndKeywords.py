class TOCWithInitsAndKeywords:
    """
    = First entry =

    TOC in somewhat strange place.

        %TOC%

    = Second =

             = 3 =

    %TOC% not replaced here
    """

    def __init__(self, arg=True):
        pass

    def keyword(self):
        """Tags: tag"""
        pass
