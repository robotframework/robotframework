import socket

__all__ = ["PORT"]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 0))
PORT = str(s.getsockname()[1])
s.close()



