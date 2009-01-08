import java.util.Hashtable;
import java.util.LinkedList;


public class ExampleJavaLibrary {

	public static final String ROBOT_LIBRARY_SCOPE = "GLOBAL";
	private int counter = 0;

    public void print(Object msg) {
    	print(msg, "INFO");
    }

    public void print(Object msg, String level) {
    	System.out.println("*" + level.toUpperCase() + "*" + msg);
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
    
    public int[] getArrayOfThreeInts() {
    	int[] ret = { 1, 2, 42 }; 
    	return ret;
    }
    
    public Hashtable getHashtable() {
    	return new Hashtable();
    }
    
    public void setToHashtable(Hashtable ht, String key, String value) {
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
        LinkedList list = new LinkedList();
    	for (int i=0; i < values.length; i++) {
            list.add(values[i]);
        }
        return list;
    }
     
}
