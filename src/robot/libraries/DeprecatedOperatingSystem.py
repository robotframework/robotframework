#  Copyright 2008-2014 Nokia Solutions and Networks
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


import OperatingSystem

OPSYS = OperatingSystem.OperatingSystem()

class DeprecatedOperatingSystem:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    delete_environment_variable = OPSYS.remove_environment_variable
    environment_variable_is_set = OPSYS.environment_variable_should_be_set
    environment_variable_is_not_set = OPSYS.environment_variable_should_not_be_set

    fail_unless_exists = OPSYS.should_exist
    fail_if_exists = OPSYS.should_not_exist
    fail_unless_file_exists = OPSYS.file_should_exist
    fail_if_file_exists = OPSYS.file_should_not_exist
    fail_unless_dir_exists = OPSYS.directory_should_exist
    fail_if_dir_exists = OPSYS.directory_should_not_exist
    fail_unless_dir_empty = OPSYS.directory_should_be_empty
    fail_if_dir_empty = OPSYS.directory_should_not_be_empty
    fail_unless_file_empty = OPSYS.file_should_be_empty
    fail_if_file_empty = OPSYS.file_should_not_be_empty

    empty_dir = OPSYS.empty_directory
    remove_dir = OPSYS.remove_directory
    copy_dir = OPSYS.copy_directory
    move_dir = OPSYS.move_directory
    create_dir = OPSYS.create_directory
    list_dir = OPSYS.list_directory
    list_files_in_dir = OPSYS.list_files_in_directory
    list_dirs_in_dir = OPSYS.list_directories_in_directory
    count_items_in_dir = OPSYS.count_items_in_directory
    count_files_in_dir = OPSYS.count_files_in_directory
    count_dirs_in_dir = OPSYS.count_directories_in_directory
