import java.lang.Object

from application import MainFrame


class LoginApplication(java.lang.Object):
    
    def start(self):
        MainFrame().show()

if __name__ == '__main__':
    LoginApplication().start()
 
