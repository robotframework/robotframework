import os

class loginlib:
	
	def __init__(self, interpreter='python'):
		application_path = os.path.join(os.path.dirname(__file__), '..', 
									    'sut', 'src', 'auth.py')
		self.cmd = interpreter + ' ' + application_path
		self.login_status = ''
	
	def create_user(self, username="", password=""):
		command_string = '%s create %s %s' % (self.cmd, username, password)
		self.login_status = os.popen(command_string).read()
	
	def attempt_to_login_with_credentials(self, username="", password=""):
		command_string = '%s login %s %s' % (self.cmd, username, password)
		self.login_status = os.popen(command_string).read()

	def status_should_be(self, status):
		if status != self.login_status.strip():
			raise AssertionError("Expected status to be '%s' but was '%s'"
								 % (status, self.login_status))
	