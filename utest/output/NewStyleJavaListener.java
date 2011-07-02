import java.util.Map;
import java.util.List;


public class NewStyleJavaListener {
    public static final String ROBOT_LISTENER_API_VERSION = "2";

    public void startSuite(String name, Map attrs) {
        System.out.println("SUITE START: " + name + " '" + attrs.get("doc") + "'");
    }

    public void endSuite(String name, Map attrs) {
        System.out.println("SUITE END: " + attrs.get("status") + " " + attrs.get("statistics"));
    }

    public void startTest(String name, Map attrs) {
        List tags = (List)attrs.get("tags");
        String tagsAsString = "";
        for (int i=0; i<tags.size(); i++) {
            tagsAsString += tags.get(i);
            if (i < tags.size() -1)
                tagsAsString += ", ";
        }
        System.out.println("TEST START: " + name + " '" + attrs.get("doc") + "' " + tagsAsString);
    }

    public void endTest(String name, Map attrs) {
        String status = attrs.get("status").toString();
        String message = "TEST END: " + status;
        if (status == "FAIL")
            message += " " + attrs.get("message");
        System.out.println(message);
    }

    public void startKeyword(String name, Map attrs) {
        List args = (List)attrs.get("args");
        String argsAsString = "[";
        for (int i=0; i<args.size(); i++) {
            argsAsString += "'" + args.get(i) + "'";
            if (i < args.size() -1)
                argsAsString += ", ";
        }
        argsAsString += "]";
        System.out.println("KW START: " + name + " " + argsAsString);
    }

    public void endKeyword(String name, Map attrs) {
        System.out.println("KW END: " + attrs.get("status"));
    }

    public void outputFile(String path) {
        printOutputFile("Output", path);
    }

    public void logFile(String path) {
        printOutputFile("Log", path);
    }

    public void reportFile(String path) {
        printOutputFile("Report", path);
    }

    public void debugFile(String path) {
        printOutputFile("Debug", path);
    }

    public void xunitFile(String path) {
        printOutputFile("XUnit", path);
    }

    public void close() {
        System.out.println("Closing...");
    }

    private void printOutputFile(String  name, String path) {
        System.out.println(name + ": " + path);
    }

}
