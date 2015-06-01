import java.util.*;

public class JavaMultipleListenerLibrary {

    public ArrayList<JavaListenerLibrary> ROBOT_LIBRARY_LISTENER;

    public JavaMultipleListenerLibrary() {
        ROBOT_LIBRARY_LISTENER = new ArrayList<JavaListenerLibrary>();
        ROBOT_LIBRARY_LISTENER.add(new JavaListenerLibrary());
        ROBOT_LIBRARY_LISTENER.add(new JavaListenerLibrary());
    }

    public void eventsShouldBe(List<String> expected) {
        for (JavaListenerLibrary instance : ROBOT_LIBRARY_LISTENER) {
            instance.eventsShouldBe(expected);
        }
    }
}
