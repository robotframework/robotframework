from robot.api import deco
from robot.errors import DataError


class EmbeddedArgs(object):

    def callables(self):
        return [getattr(self, f) for f in dir(self) if callable(getattr(self, f))]

    def get_keyword_names(self):
        return [f.robot_name for f in self.callables() if hasattr(f, 'robot_name')]

    def run_keyword(self, name, args):
        if '$' in name:
            match = [f for f in self.callables() if getattr(f, 'robot_name', None) == name]
            if len(match) == 1:
                f = match[0]
            else:
                raise DataError("No single match for '%s' could be found" % name)
        else:
            f = getattr(self, name)
        return f(*args)

    @deco.keyword('Add ${count} Copies Of ${item} To Cart')
    def add_copies_to_cart(self, count, item):
        return count, item
