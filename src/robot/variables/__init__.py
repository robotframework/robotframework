#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

"""Implements storing and resolving variables.

This package is mainly for internal usage.
"""

from .assigner import VariableAssignment
from .isvar import contains_var, is_var, is_scalar_var, is_list_var, is_dict_var
from .notfound import variable_not_found
from .scopes import VariableScopes
from .splitter import VariableSplitter, VariableIterator
from .tablesetter import VariableTableValue, DictVariableTableValue
from .variables import Variables
