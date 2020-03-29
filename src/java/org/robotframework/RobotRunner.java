/* Copyright 2008-2015 Nokia Networks
 * Copyright 2016-     Robot Framework Foundation
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
 * AutoCloseable Interface class that internally creates a Jython interpreter,
 * allows running Robot tests with it, and cleans up the interpreter afterwards
 * in close.<p>
 *
 * Example:
 * <pre>
 *
 * {@code
 * try (RobotRunner runner = new RobotRunner()) {
 *     runner.run(new String[] {"tests.robot"});
 * }
 * }
 * </pre>
 */
public class RobotRunner implements AutoCloseable {

    private RobotPythonRunner runner;
    private PythonInterpreter interpreter;

    public RobotRunner() {
        interpreter = new PythonInterpreter();
        runner = createRunner();
    }

    /**
     * Creates and returns an instance of the robot.JarRunner (implemented in
     * Python), which can be used to execute tests.
     */
    private RobotPythonRunner createRunner() {
        PyObject runnerClass = importRunnerClass();
        PyObject runnerObject = runnerClass.__call__();
        return (RobotPythonRunner) runnerObject.__tojava__(RobotPythonRunner.class);
    }

    private PyObject importRunnerClass() {
        interpreter.exec(
            "from robot.jarrunner import JarRunner, process_jythonpath\n" +
            "process_jythonpath()"
        );
        return interpreter.get("JarRunner");
    }

    /**
     * Runs the tests, but does not cleanup the interpreter afterwards.
     *
     * @param args
     *              The command line options to Robot Framework.
     *
     * @return      Robot Framework return code. See
     *              <a href="http://robotframework.org/robotframework/#user-guide"
     *                 target="_top">Robot Framework User Guide</a>
     *              for meaning of different return codes.
     */
    public int run(String[] args) {
        return runner.run(args);
    }

    /**
     * Cleans up the Jython interpreter.
     */
    public void close() {
        interpreter.cleanup();
    }
}
