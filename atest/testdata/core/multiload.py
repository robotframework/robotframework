from robot.api import logger

_global_num = None

class multiload():

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, num):
        global _global_num
        _global_num = num
        self.num = num

    def get_num(self):
        return self.num
    
    def get_global_num(self):
        global _global_num
        return _global_num

