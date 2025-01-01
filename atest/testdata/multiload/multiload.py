from robot.api import logger

class multiload():

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, num):
        self.num = num

    def get_num(self):
        return self.num
