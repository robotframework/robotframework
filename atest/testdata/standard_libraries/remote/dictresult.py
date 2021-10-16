import sys

from remoteserver import RemoteServer


class DictResult:

    def return_dict(self, **kwargs):
        return kwargs

    def return_nested_dict(self):
        return dict(key='root', nested=dict(key=42, nested=dict(key='leaf')))

    def return_dict_in_list(self):
        return [{'foo': 1}, self.return_nested_dict()]


if __name__ == '__main__':
    RemoteServer(DictResult(), *sys.argv[1:])
