import java.io.*;
import java.util.*;
import org.python.core.*;


public class JavaAttributeVerifyingListener {
    public static final String ROBOT_LISTENER_API_VERSION = "2";
    private BufferedWriter outfile;
    private Map expectedTypes;

    public JavaAttributeVerifyingListener() throws IOException {
        createOutputFile();
        createExpectedTypes();
    }

    public void createOutputFile() throws IOException {
        String tmpdir = JavaTempDir.getTempDir();
        String sep = System.getProperty("file.separator");
        String outpath = tmpdir + sep + "listener_attrs_java.txt";
        outfile = new BufferedWriter(new FileWriter(outpath));
    }

    public void createExpectedTypes() {
        expectedTypes = new HashMap<String, Class>() {{
                put("elapsedtime", Integer.class);
                put("tags", PyList.class);
                put("args", PyList.class);
                put("assign", PyList.class);
                put("metadata", PyDictionary.class);
                put("tests", PyList.class);
                put("suites", PyList.class);
                put("totaltests", Integer.class);
                put("lineno", Integer.class);
            }};
    }

    public void startSuite(String name, Map attrs) {
        verifyAttributes("START SUITE", attrs,
                         new String[] {"id", "doc", "starttime", "longname",  "source", "metadata", "tests", "suites", "totaltests"});
    }

    public void endSuite(String name, Map attrs) {
        verifyAttributes("END SUITE", attrs,
                         new String[] {"id", "doc", "starttime", "longname",  "source", "metadata", "tests", "suites", "totaltests", "endtime", "elapsedtime", "status", "message", "statistics"});
    }

    public void startTest(String name, Map attrs) {
        verifyAttributes("START TEST", attrs,
                         new String[] {"id", "doc", "starttime", "longname", "origname", "tags", "template", "source", "lineno"});
    }

    public void endTest(String name, Map attrs) {
        verifyAttributes("END TEST", attrs,
                         new String[] {"id", "doc", "starttime", "longname", "origname", "tags", "template", "source", "lineno", "endtime", "elapsedtime", "status", "message"});
    }

    public void startKeyword(String name, Map attrs) {
        verifyAttributes("START KEYWORD", attrs,
                         new String[] {"type", "kwname", "libname", "doc", "args", "assign", "tags", "source", "lineno", "status", "starttime"});
    }

    public void endKeyword(String name, Map attrs) {
        verifyAttributes("END KEYWORD", attrs,
                         new String[] {"type", "kwname", "libname", "doc", "args", "assign", "tags", "source", "lineno", "status", "starttime", "endtime", "elapsedtime"});
    }

    public void close() throws IOException {
        outfile.close();
    }

    private void verifyAttributes(String methodName, Map attrs, String[] names) {
        try {
            outfile.write(methodName + "\n");
            if (attrs.size() != names.length) {
                outfile.write("FAILED: wrong number of attributes\n");
                outfile.write("Expected: " + Arrays.toString(names) + "\n" + "Actual:   " + attrs.keySet() + "\n");
            }
            else {
                for (String name: names) {
                    if (name.equals("origname"))
                        continue;
                    Object attr = attrs.get(name);
                    String status = "PASSED";
                    Class expectedClass = Class.forName("java.lang.String");
                    if (expectedTypes.containsKey(name))
                        expectedClass = (Class)expectedTypes.get(name);
                    if (!(attr.getClass()).equals(expectedClass))
                        status = "FAILED";
                    outfile.write(status + " | " + name + ": " + attr.getClass() + "\n");
                }
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
