package org.robotframework;

import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

public class RunnerFactory {

    private PyObject runnerClass;

    public RunnerFactory() {
        runnerClass = importRunnerClass();
    }
    
	private PyObject importRunnerClass() {
		PythonInterpreter interpreter = new PythonInterpreter();
        interpreter.exec("import robot; from robot.jarrunner import JarRunner");
        return interpreter.get("JarRunner");
	}

    public RobotRunner createRunner() {
        PyObject runnerObject = runnerClass.__call__();
        return (RobotRunner)runnerObject.__tojava__(RobotRunner.class);
    }
}
