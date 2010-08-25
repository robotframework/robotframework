package org.robotframework;

import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

/**
 *
 * Helper class to create an Jython object and coerce it so that it can be used
 * from Java.
 *
 */
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

    /**
     * Creates and returns an instance of the robot.JarRunner (implemented in
     * Python), which can be used to execute tests.
     */
    public RobotRunner createRunner() {
        PyObject runnerObject = runnerClass.__call__();
        return (RobotRunner) runnerObject.__tojava__(RobotRunner.class);
    }
}
