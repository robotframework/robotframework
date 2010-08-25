package org.robotframework;

/**
 * An interface class that is used for creating a Jython object capable of
 * running Robot Framework.
 */
public interface RobotRunner {

    public int run(String[] args);

}
