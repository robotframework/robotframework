class DeprecatedKeywords:

    def deprecated_library_keyword(self):
        """*DEPRECATED* Use keyword `Not Deprecated With Doc` instead!

        Some more doc here. ignore this in the warning.
        """
        pass

    def deprecated_library_keyword_without_extra_doc(self):
        """*DEPRECATED*"""
        pass

    def deprecated_library_keyword_with_stuff_to_ignore(self):
        """*DEPRECATED ignore this stuff*"""
        pass

    def deprecated_keyword_returning(self):
        """*DEPRECATED.* But still returning a value!"""
        return 42

    def not_deprecated_with_doc(self):
        """Some Short Doc

        Some more doc and ignore this *DEPRECATED*
        """
        pass

    def not_deprecated_with_deprecated_prefix(self):
        """*DEPRECATED ... just kidding!!"""
        pass

    def not_deprecated_without_doc(self):
        pass
