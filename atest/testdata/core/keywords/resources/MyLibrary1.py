class MyLibrary1:

    def keyword_only_in_library_1(self):
        print "Keyword from library 1"

    def keyword_in_both_libraries(self):
        print "Keyword from library 1"
        
    def keyword_in_all_resources_and_libraries(self):
        print "Keyword from library 1"

    def keyword_everywhere(self):
        print "Keyword from library 1"

    def keyword_in_tc_file_overrides_others(self):
        raise Exception("This keyword should not be called")

    def keyword_in_resource_overrides_libraries(self):
        raise Exception("This keyword should not be called")
    
    def comment(self):
        print "Overrides keyword from BuiltIn library"
        
    def copy_directory(self):
        print "Overrides keyword from OperatingSystem library"
 
    def no_operation(self):
        print "Overrides keyword from BuiltIn library"