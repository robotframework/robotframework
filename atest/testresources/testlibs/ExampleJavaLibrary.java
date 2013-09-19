import java.util.Hashtable;
import java.util.LinkedList;
import java.util.List;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.util.Vector;
import java.util.Iterator;


public class ExampleJavaLibrary {
    public static final String ROBOT_LIBRARY_SCOPE = "GLOBAL";
    private int counter = 0;

    public void print(Object msg) {
        System.out.println(msg);
    }

    public void print(Object msg, String level) {
        System.out.println("*" + level.toUpperCase() + "*" + msg);
    }

    public void stderr(Object msg) {
        System.err.println(msg);
    }

    public void stderr(Object msg, String level) {
        System.err.println("*" + level.toUpperCase() + "* " + msg);
    }

    public void divByZero() {
        int i = 1/0;
    }

    public void javaException() {
        exception(null);
    }

    public void javaException(String msg) {
        exception(msg);
    }

    // Jython creates properties from getters, which should not be accessed
    // at library creation time. See issue 188.
    public int getCount() {
        counter++;
        return counter;
    }

    private void exception(String msg) {
        throw new ArrayStoreException(msg);
    }

    public void externalJavaException() {
        new JavaObject().exception();
    }

    public void javaSleep(String secs) throws InterruptedException {
        javaSleep(Double.parseDouble(secs));
    }

    public void javaSleep(double secs) throws InterruptedException {
        int millis = (new Double(secs * 1000)).intValue();
        Thread.sleep(millis);
        System.out.println("Slept " + secs + " seconds in Java");
    }

    public void printMultipleMessagesAndSleepBetween() throws InterruptedException {
        System.out.println("First message.");
        Thread.sleep(42);
        System.out.println("Secong line of the first message.");
        System.out.println("*WARN* Looping and sleeping next..");
        System.out.print("*INFO*");
        for (int i=0; i < 100; i++) {
            System.out.print(i);
            Thread.sleep(2);
        }
    }

    public String returnStringFromLibrary(String s) {
        return s;
    }

    public JavaObject getJavaObject(String name) {
        return new JavaObject(name);
    }

    public String[] getStringArray(String[] args) {
        return args;
    }

    public Vector getStringVector(String[] args) {
        return new Vector<String>(Arrays.asList(args));
    }

    public List<String> getStringList(String[] args) {
        return Arrays.asList(args);
    }

    public Iterator<String> getStringIterator(String[] args) {
        return Arrays.asList(args).iterator();
    }

    public ArrayList<String> getStringArrayList(String[] args) {
        ArrayList<String> list = new ArrayList<String>();
        for (String s : args)
            list.add(s);
        return list;
    }

    public int[] getArrayOfThreeInts() {
        int[] ret = { 1, 2, 42 };
        return ret;
    }

    public Hashtable getHashtable() {
        return new Hashtable();
    }

    public void setToHashtable(Hashtable<String, String> ht, String key, String value) {
        ht.put(key, value);
    }

    public String getFromHashtable(Hashtable ht, String key) {
        return (String)ht.get(key);
    }

    public void checkInHashtable(Hashtable ht, String key, String expected) {
        String actual = (String)ht.get(key);
        if (!actual.equals(expected)) {
            throw new AssertionError(actual + " != " + expected);
        }
    }

    public LinkedList getLinkedList(Object[] values) {
        LinkedList<Object> list = new LinkedList<Object>();
        for (int i=0; i < values.length; i++) {
            list.add(values[i]);
        }
        return list;
    }

    public Object returnUnrepresentableObject() {
        return new Object() {
            public String toString() {
                throw new RuntimeException("failure in toString");
            }
        };
    }

    public void failWithSuppressedExceptionNameInJava(String msg) {
        throw new MyJavaException(msg);
    }


    public class MyJavaException extends RuntimeException {
        public static final boolean ROBOT_SUPPRESS_NAME = true;

        public MyJavaException(String msg) {
            super(msg);
        }
    }
}
