import os
import sys
from stat import *


class TestHelper:
    
    def set_read_only(self, path):
        os.chmod(path, S_IREAD)

    def set_read_write(self, path):
        os.chmod(path, S_IREAD | S_IWRITE)

    def get_output_name(self, name, *datasources):
        if name is not None:
            return name
        elif len(datasources) == 1:
            return self._get_name(datasources[0])
        else:
            names = [ self._get_name(source) for source in datasources ]
            return '_'.join(names)
        
    def _get_name(self, path):
        return os.path.splitext(os.path.basename(path))[0]
