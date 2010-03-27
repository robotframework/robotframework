import java.io.*;
import java.util.*;
import java.math.BigInteger;
import org.python.core.PyList;
import org.python.core.PyDictionary;

public class JavaAttributeVerifyingListener {
    public static final String ROBOT_LISTENER_API_VERSION = "2";
	private BufferedWriter outfile;
	private Map expectedTypes; 
	
	public JavaAttributeVerifyingListener() throws IOException {
		createOutputFile();
		createExcpectedTypes();
	}

	public void createOutputFile() throws IOException {
		String tmpdir = System.getProperty("java.io.tmpdir");
		String sep = System.getProperty("file.separator");
		String outpath = tmpdir + sep + "listener_attrs_java.txt";
		outfile = new BufferedWriter(new FileWriter(outpath));
	}
	public void createExcpectedTypes() {
		expectedTypes = new HashMap();
		expectedTypes.put("elapsedtime", BigInteger.class);
		expectedTypes.put("tags", PyList.class);
		expectedTypes.put("args", PyList.class);
		expectedTypes.put("metadata", PyDictionary.class);
	}
	
	public void startSuite(String name, Map attrs) {
		verifyAttributes("START SUITE", attrs,
                         new String[] {"doc", "starttime", "longname", "metadata"});
	}

	public void endSuite(String name, Map attrs) {
		verifyAttributes("END SUITE", attrs, new String[] {"doc", "starttime", "longname", "endtime", "elapsedtime", "status", "message", "statistics"});
	}
	
	public void startTest(String name, Map attrs) {
		verifyAttributes("START TEST", attrs, new String[] {"doc", "starttime", "longname", "tags"});	
	}

	public void endTest(String name, Map attrs) {
		verifyAttributes("END TEST", attrs, new String[] {"doc", "starttime", "longname", "tags", "endtime", "elapsedtime", "status", "message"});	
	}
	
	public void startKeyword(String name, Map attrs) {
		verifyAttributes("START KEYWORD", attrs, new String[] {"doc", "starttime", "args"});	
	}
	
	public void endKeyword(String name, Map attrs) {
		verifyAttributes("END KEYWORD", attrs, new String[] {"doc", "starttime", "args", "endtime", "elapsedtime", "status"});	
	}

	public void close() throws IOException {
		outfile.close();
	}

	private void verifyAttributes(String methodName, Map attrs, String[] names) {
		try {
			outfile.write(methodName + "\n");
			if (attrs.size() != names.length) {
        		outfile.write("FAILED: wrong number of attributes\n");
        		outfile.write("Expected: " + names + "\n" + "Actual: " + attrs.keySet() + "\n");
			}
			else {
				for (int i=0; i<names.length; i++){
					String name = names[i];
					Object attr = attrs.get(name);
					String status = "PASSED";
					Class expectedClass = Class.forName("java.lang.String");	
					if (expectedTypes.containsKey(name))
						expectedClass = (Class)expectedTypes.get(name);
					if (!(attr.getClass()).equals(expectedClass)) {
						status = "FAILED";
					}
					outfile.write(status + " | " + name + ": " + attr.getClass() + "\n");
				}	
			}
		} catch (Exception e) {
			throw new RuntimeException(e);
		}	
			
	}  
}
