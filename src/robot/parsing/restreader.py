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


def read_rest(rstfile):
    from .restsupport import publish_doctree, RobotDataStorage

    doctree = publish_doctree(
        rstfile.read(), source_path=rstfile.name,
        settings_overrides={
            'input_encoding': 'UTF-8',
            'report_level': 4
        })
    store = RobotDataStorage(doctree)
    return store.get_data()

