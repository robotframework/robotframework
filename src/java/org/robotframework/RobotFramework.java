/* Copyright 2008-2012 Nokia Siemens Networks Oyj
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

import org.robotframework.RunnerFactory;
import org.robotframework.RobotRunner;

/**
 * 
 * Entry point for using Robot Framework from Java programs.
 * 
 */
public class RobotFramework {

    public static void main(String[] args) {
        int rc = run(args);
        System.exit(rc);
    }

    /**
     * Runs Robot Framework tests.
     * 
     * @param args
     *            The command line options to Robot Framework, for example
     *            ['--outputdir', '/tmp', 'mytestdir']. At least one datasource
     *            must be specified.
     */
    public static int run(String[] args) {
        RobotRunner runner = new RunnerFactory().createRunner();
        return runner.run(args);
    }
}
