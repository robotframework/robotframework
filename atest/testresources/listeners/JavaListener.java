import java.io.*;
import java.util.Map;
import java.util.List;


public class JavaListener {

    public static final String ROBOT_LISTENER_API_VERSION = "2";

    BufferedWriter outfile = null;

    public JavaListener() throws IOException {
        String tmpdir = JavaTempDir.getTempDir();
        String sep = System.getProperty("file.separator");
        String outpath = tmpdir + sep + "listen_java.txt";
        this.outfile = new BufferedWriter(new FileWriter(outpath ));
    }

    public void startSuite(String name, Map attrs) throws IOException {
        Map metadata = (Map)attrs.get("metadata");
        String metastr = getMetaString(metadata);
        this.outfile.write("START SUITE: " + name + " '" + attrs.get("doc")
                           + "' " + metastr + "\n");
    }

    private String getMetaString(Map metadata) {
        String metastr = "[";
        for (Object obj: metadata.entrySet()) {
            Map.Entry entry = (Map.Entry) obj;
            metastr += entry.getKey() + ": " + entry.getValue();
        }
        metastr += "]";
        return metastr;
    }

    public void startTest(String name, Map attrs) throws IOException {
        this.outfile.write("START TEST: " + name + " '" + attrs.get("doc") + "' [");
        List tags = (List)attrs.get("tags");
        for (int i=0; i < tags.size(); i++) {
            this.outfile.write(tags.get(i).toString());
        }
        this.outfile.write("]\n");
    }

    public void startKeyword(String name, Map attrs) throws IOException {
        this.outfile.write("START KW: " + name + " [");
        List args = (List)attrs.get("args");
        for (int i=0; i < args.size(); i++) {
            this.outfile.write(args.get(i).toString());
        }
        this.outfile.write("]\n");
    }

    public void logMessage(Map message) throws IOException {
        String msg = (String)message.get("message");
        String level = (String)message.get("level");
        String html = (String)message.get("html");
        String timestamp = (String)message.get("timestamp");
        if (!html.equals("yes") && !html.equals("no")) {
            this.outfile.write("Log message has invalid `html` attribute " + html);
        }
        if (!level.equals("TRACE") && msg.indexOf("Traceback") < 0) {
            this.outfile.write("LOG MESSAGE: [" + level + "] " + msg + "\n");
        }
    }

    public void message(Map message) throws IOException {
        String msg = (String)message.get("message");
        String level = (String)message.get("level");
        String html = (String)message.get("html");
        String timestamp = (String)message.get("timestamp");
        if (!html.equals("yes") && !html.equals("no")) {
            this.outfile.write("Log message has invalid `html` attribute " + html);
        }
        if (msg.indexOf("Settings") >= 0) {
            this.outfile.write("Got settings on level: " + level + "\n");
        }
    }

    public void endTest(String name, Map attrs) throws IOException {
        String status = attrs.get("status").toString();
        if (status.equals("PASS")) {
            this.outfile.write("END TEST: " + status + "\n");
        }
        else {
            this.outfile.write("END TEST: " + status + ": " + attrs.get("message") + "\n");
        }
    }

    public void endSuite(String name, Map attrs) throws IOException {
        this.outfile.write("END SUITE: " + attrs.get("status") + ": " + attrs.get("statistics") + "\n");
    }

    public void outputFile(String path) throws IOException {
        this.writeOutputFile("Output", path);
    }

    public void reportFile(String path) throws IOException {
        this.writeOutputFile("Report", path);
    }

    public void logFile(String path) throws IOException {
        this.writeOutputFile("Log", path);
    }

    public void debugFile(String path) throws IOException {
        this.writeOutputFile("Debug", path);
    }

    public void close() throws IOException {
        this.outfile.write("The End\n");
        this.outfile.close();
    }

    private void writeOutputFile(String name, String path) throws IOException {
        File f = new File(path);
        this.outfile.write(name + " (java): " + f.getName() + "\n");
    }
}
