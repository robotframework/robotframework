#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from robot.result.builders import ResultFromXML
try:
    import psutil
    import objgraph
except ImportError:
    print """
    Please install psutil and objgraph - this script does not work without them.
    """
    raise

def calculate_rebot_model(output_path):
    xml = ResultFromXML(output_path)
    p = psutil.Process(os.getpid())
    print 'Process memory usage after xml parsing %f M' % (float(p.get_memory_info().rss) / (1024**2))
    print 'Most common types'
    objgraph.show_most_common_types()
    return xml

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print """
        Simple memory profiler for robot output xml parsing.
        Calculates memory usages after result model has been created.
        usage:
        calculate_rebot_model.py [PATH_TO_OUTPUT_XML]
        """
    else:
        calculate_rebot_model(sys.argv[1])
