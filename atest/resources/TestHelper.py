import os
import sys
from stat import S_IREAD, S_IWRITE


class TestHelper:
    
    def set_read_only(self, path):
        os.chmod(path, S_IREAD)

    def set_read_write(self, path):
        os.chmod(path, S_IREAD | S_IWRITE)

    def get_output_name(self, *datasources):
        if not datasources:
            raise RuntimeError('One or more data sources must be given!')
        if len(datasources) == 1:
            return self._get_name(datasources[0])
        return '_'.join(self._get_name(source) for source in datasources)
        
    def _get_name(self, path):
        return os.path.splitext(os.path.basename(path))[0]
    
    def should_contain_item_x_times(self, string, item, count):
        if string.count(item) != int(count):
            raise AssertionError("'%s' does not contain '%s' '%s' "
                                 "times!" % (string, item, count))

    def get_splitted_full_name(self, full_name, splitlevel):
        splitlevel = int(splitlevel)
        parts = full_name.split('.')
        if splitlevel > 0 and splitlevel <= len(parts):
            parts = parts[splitlevel:]
        return '.'.join(parts)