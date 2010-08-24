package org.robotframework;

import org.robotframework.RunnerFactory;
import org.robotframework.RobotRunner;

public class JarRobot {

	public static void main(String[] args) {
        int rc = run(args);
        System.exit(rc);
    }

	public static int run(String[] args) {
		RobotRunner runner = new RunnerFactory().createRunner();
        return runner.run(args);
	}
}
