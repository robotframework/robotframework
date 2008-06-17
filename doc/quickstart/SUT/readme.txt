This directory contains the source and unit tests for the login example tested in the Quick Start Guide tests.

To run the example from this directory, start by entering the command:

ruby src/auth.rb login yourname yourpassword

(Substitute your name and desired password.)

You should receive a response on standard out: "Access Denied."

Now try creating yourself an account:

ruby src/auth.rb create yourname yourpassword

You should see "SUCCESS" on standard out.

And now you can log in.  If you enter the command ruby src/auth.rb login yourname yourpassword again, you should see the response "Logged In."

