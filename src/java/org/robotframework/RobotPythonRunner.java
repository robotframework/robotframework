package org.robotframework;

/**
 * Interface used by {@link org.robotframework.RobotRunner} internally to
 * construct the Robot Framework Python class.
 */
public interface RobotPythonRunner {

    public int run(String[] args);

}
