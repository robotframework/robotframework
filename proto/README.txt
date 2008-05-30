Prototypes
==========

The subdirectories of this directory contain possible additions and tools
for Robot Framework that are either untested or not otherwise not ready.

schema /
    Contains a somewhat outdated schema of Robot Framewrk output
	file in RelaxNG format.

xmlrpc/
	Contains a prototype implementation of XML-RPC library allowing 
    communication between Robot Framework and remote libraries implemented 
    using any language supporting XML-RPC. The directory contains the library
    to be used with Robot Framework (RobotXmlRpc.py) and remote library 
    prototypes implemented both with Ruby and Python.

run_acceptance_tests.sh
    Our old script for running acceptance tests from CruiseControl.
