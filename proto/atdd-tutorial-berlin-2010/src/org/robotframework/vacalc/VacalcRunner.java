package org.robotframework.vacalc;

import org.python.core.PyObject;
import org.python.util.PythonInterpreter;
import org.robotframework.vacalc.VacationCalculator;

public class VacalcRunner {

    public static void main(String[] args) {
        vacalcApplication().create();
    }

    private static VacationCalculator vacalcApplication() {
        PyObject application = importAppClass().__call__();
        return (VacationCalculator) application.__tojava__(VacationCalculator.class);
    } 

    private static PyObject importAppClass() {
        PythonInterpreter interpreter = new PythonInterpreter();
        interpreter.exec("import vacalc; from vacalc import VacalcApplication");
        return interpreter.get("VacalcApplication");
    }
}
