import commands

SRC_PATH = 'ruby SUT/src/auth.rb'

class loginlib:
	login_status = ''
	
	def create_user(self, username="", password=""):
		command_string = '%s create %s %s' % (SRC_PATH, username, password)
		self.login_status = commands.getoutput(command_string)
	
	def attempt_to_login_with_credentials(self, username="", password=""):
		command_string = '%s login %s %s' % (SRC_PATH, username, password)
		self.login_status = commands.getoutput(command_string)

	def status_should_be(self, status):
		if status != self.login_status:
			raise AssertionError("Expected status to be '%s' but was '%s'"
								 % (status, self.login_status))
	