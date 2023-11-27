import os
from pathlib import Path


VERSION_FILE = Path(os.getenv('TEMPDIR'), 'listener-versions.txt')


class V2:
    ROBOT_LISTENER_API_VERSION = 2

    def start_suite(self, name, attrs):
        assert name == attrs['longname'] == 'Pass And Fail'
        with open(VERSION_FILE, 'a') as f:
            f.write(type(self).__name__ + '\n')


class V2AsNonInt(V2):
    ROBOT_LISTENER_API_VERSION = '2'


class V3Implicit:

    def start_suite(self, data, result):
        assert data.name == result.name == 'Pass And Fail'
        with open(VERSION_FILE, 'a') as f:
            f.write(type(self).__name__ + '\n')


class V3Explicit(V3Implicit):
    ROBOT_LISTENER_API_VERSION = 3


class V3AsNonInt(V3Implicit):
    ROBOT_LISTENER_API_VERSION = 3.3
