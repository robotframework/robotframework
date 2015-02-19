#  Copyright 2008-2015 Nokia Solutions and Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from .DeprecatedBuiltIn import deprecator
from .OperatingSystem import OperatingSystem


OS = OperatingSystem()


class DeprecatedOperatingSystem(object):
    __metaclass__ = deprecator

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    delete_environment_variable = OS.remove_environment_variable
    environment_variable_is_set = OS.environment_variable_should_be_set
    environment_variable_is_not_set = OS.environment_variable_should_not_be_set

    fail_unless_exists = OS.should_exist
    fail_if_exists = OS.should_not_exist
    fail_unless_file_exists = OS.file_should_exist
    fail_if_file_exists = OS.file_should_not_exist
    fail_unless_dir_exists = OS.directory_should_exist
    fail_if_dir_exists = OS.directory_should_not_exist
    fail_unless_dir_empty = OS.directory_should_be_empty
    fail_if_dir_empty = OS.directory_should_not_be_empty
    fail_unless_file_empty = OS.file_should_be_empty
    fail_if_file_empty = OS.file_should_not_be_empty

    empty_dir = OS.empty_directory
    remove_dir = OS.remove_directory
    copy_dir = OS.copy_directory
    move_dir = OS.move_directory
    create_dir = OS.create_directory
    list_dir = OS.list_directory
    list_files_in_dir = OS.list_files_in_directory
    list_dirs_in_dir = OS.list_directories_in_directory
    count_items_in_dir = OS.count_items_in_directory
    count_files_in_dir = OS.count_files_in_directory
    count_dirs_in_dir = OS.count_directories_in_directory
