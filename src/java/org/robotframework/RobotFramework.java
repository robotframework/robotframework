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

/**
 *
 * Entry point for using Robot Framework from Java programs.
 *
 */
public class RobotFramework {

    /**
     * Entry point when used as a main program. Uses
     * {@link #run} to run Robot Framework and calls
     * {@link java.lang.System#exit} with the return code.
     *
     * @param args
     *              The command line options, passed to <code>run</code>.
     */
    public static void main(String[] args) {
        int rc = run(args);
        System.exit(rc);
    }

    /**
     * Runs Robot Framework.<p>
     *
     * The default action is to run tests, but it is also possible to use
     * other RF functionality by giving a command as a first value in
     * <code>args</code>. The available commands are <ul><li>rebot</li>
     * <li>libdoc</li><li>tidy</li><li>testdoc</li></ul><p>
     *
     * Example usages:<br>
     * <code>run(new String[] {"--outputdir", "/tmp", "tests.robot"})</code><br>
     * <code>run(new String[] {"libdoc", "MyLibrary", "mydoc.html"})</code>
     *
     * @param args
     *              The command line options to Robot Framework.
     *
     * @return      Robot Framework return code. See
     *              <a href="http://robotframework.org/robotframework/#user-guide"
                       target="_top">Robot Framework User Guide</a>
     *              for meaning of different return codes.
     */
    public static int run(String[] args) {
        try (RobotRunner runner = new RobotRunner()) {
            return runner.run(args);
        }
    }
}
