/* Copyright 2008-2015 Nokia Solutions and Networks
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

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
    public PythonInterpreter interpreter;

    public RunnerFactory() {
        interpreter = new PythonInterpreter();
        runnerClass = importRunnerClass();
    }

    private PyObject importRunnerClass() {
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

    /**
     * Cleans up the interpreter used for creating runners.
     */
    public void cleanup() {
        interpreter.cleanup();
    }
}
