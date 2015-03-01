# coding=UTF-8

from __future__ import print_function

from robot.api.deco import keyword


class MyLibrary1:

    def keyword_only_in_library_1(self):
        print("Keyword from library 1")

    def keyword_in_both_libraries(self):
        print("Keyword from library 1")

    def keyword_in_all_resources_and_libraries(self):
        print("Keyword from library 1")

    def keyword_everywhere(self):
        print("Keyword from library 1")

    def keyword_in_tc_file_overrides_others(self):
        raise Exception("This keyword should not be called")

    def keyword_in_resource_overrides_libraries(self):
        raise Exception("This keyword should not be called")

    def comment(self):
        print("Overrides keyword from BuiltIn library")

    def copy_directory(self):
        print("Overrides keyword from OperatingSystem library")

    def no_operation(self):
        print("Overrides keyword from BuiltIn library")

    def method(self):
        print("My name was set using 'robot_name' attribute!")

    method.robot_name = "Name set using 'robot_name' attribute"

    @keyword("Name set using 'robot.api.deco.keyword' decorator")
    def name_set_in_method_signature(self):
        print("My name was set using 'robot.api.deco.keyword' decorator!")

    @keyword(name=u'Custom nön-ÄSCII name')
    def non_ascii_would_not_work_here(self):
        pass

    @keyword()
    def no_custom_name_given_1(self):
        pass

    @keyword
    def no_custom_name_given_2(self):
        pass
