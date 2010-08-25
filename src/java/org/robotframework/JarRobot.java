package org.robotframework;

import org.robotframework.RunnerFactory;
import org.robotframework.RobotRunner;

/**
 *
 * Entry point for using Robot Framework from Java programs.
 *
 */

public class JarRobot {

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
