class ParameterLibrary:
    
    def __init__(self, host='localhost', port='8080'):
        self.host = host
        self.port = port
        
    def parameters(self):
        return self.host, self.port