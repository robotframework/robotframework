Prototypes
==========

This directory contains possible additions and tools for Robot Framework 
that are either untested or otherwise not yet ready for real use.

schema /
    Contains a somewhat outdated schema of Robot Framewrk output
	file in RelaxNG format.

remote/
    Contains a prototype implementation of a remote library  allowing 
    communication between Robot Framework and remote libraries implemented 
    using any language supporting XML-RPC. The directory contains the library
    to be used with Robot Framework (RobotRemoteLibrary.py) and remote library 
    prototypes implemented both with Ruby and Python.

run_acceptance_tests.sh
    Our old script for running acceptance tests from CruiseControl.
