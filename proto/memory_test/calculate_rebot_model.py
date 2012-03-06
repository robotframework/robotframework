import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from robot.reporting.outputparser import OutputParser
from robot.result.builders import ResultFromXML
try:
    import psutil
    import objgraph
except ImportError:
    print """
    Please install psutil and objgraph - this script does not work without them.
    """
    raise

def calculate_rebot_model(args):
    if args[0] == '--reference':
        xml = OutputParser().parse(args[1])
    else:
        xml = ResultFromXML(args[0])
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
        --reference will calculate using list model implementation.
        usage:
        calculate_rebot_model.py [PATH_TO_OUTPUT_XML]
        calculate_rebot_model.py --reference [PATH_TO_OUTPUT_XML]
        """
    else:
        calculate_rebot_model(sys.argv[1:])
