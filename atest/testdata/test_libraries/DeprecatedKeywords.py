class DeprecatedKeywords:
    
    def deprecated_library_keyword(self):
        """*DEPRECATED* Use keyword `Not Deprecated With Doc` instead!
        
        Some more doc here which is ignored in the warning.
        """
        pass

    def deprecated_keyword_returning(self):
        """*DEPRECATED* But still returning a value!"""
        return 42
    
    def not_deprecated_with_doc(self):
        """Some Short Doc
        
        Some more doc and ignore this *DEPRECATED*
        """
        pass
    
    def not_deprecated_without_doc(self):
        pass
