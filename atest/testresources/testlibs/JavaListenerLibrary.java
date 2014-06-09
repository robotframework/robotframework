import java.util.*;

public class JavaListenerLibrary {

    public static final String ROBOT_LISTENER_API_VERSION = "2";
    public static final String ROBOT_LIBRARY_SCOPE = "TEST SUITE";

    public ArrayList<String> events = new ArrayList<String>();

    public JavaListenerLibrary ROBOT_LIBRARY_LISTENER;

    public JavaListenerLibrary() {
        ROBOT_LIBRARY_LISTENER = this;
    }

    public void startSuite(String name, Map attrs){
        events.add("start suite "+name);
    }

    public void endSuite(String name, Map attrs){
        events.add("end suite "+name);
    }

    public void startTest(String name, Map attrs){
        events.add("start test "+name);
    }

    public void endTest(String name, Map attrs){
        events.add("end test "+name);
    }

    public void _startKeyword(String name, Map attrs){
        events.add("start kw "+name);
    }

    public void _endKeyword(String name, Map attrs){
        events.add("end kw "+name);
    }

    public void close() {
        System.err.println("CLOSING IN JAVA SUITE LIBRARY LISTENER");
    }

    @SuppressWarnings("unchecked")
    public List<String> getEvents() {
        return (List<String>)events.clone();
    }

    public void eventsShouldBe(List<String> expected) {
        if (events.size() != expected.size())
            throw new RuntimeException("Expected events not the same size. Expected:\n"+expected+"\nActual:\n"+events);
        for (int i = 0; i < expected.size(); i++) {
            if (!expected.get(i).equals(events.get(i)))
                throw new RuntimeException("Expected events not the same. Expected:\n"+expected.get(i)+"\nActual:\n"+events.get(i));
        }

    }
}
