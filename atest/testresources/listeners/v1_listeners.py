def close():
    pass

class V1ClassListener:
    ROBOT_LISTENER_API_VERSION = 1

    def close(self):
        self.outfile.close()
