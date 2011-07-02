import java.io.*;


public class OldJavaListener {

    BufferedWriter outfile = null;

    public OldJavaListener() throws IOException {
        String tmpdir = JavaTempDir.getTempDir();
        String sep = System.getProperty("file.separator");
        String outpath = tmpdir + sep + "listen_java.txt";
        this.outfile = new BufferedWriter(new FileWriter(outpath ));
    }

    public void startSuite(String name, String doc) throws IOException {
        this.outfile.write("START SUITE: " + name + " '" + doc + "'\n");
    }

    public void startTest(String name, String doc, String[] tags) throws IOException {
        this.outfile.write("START TEST: " + name + " '" + doc + "' [");
        for (int i=0; i < tags.length; i++) {
            this.outfile.write(tags[i]);
        }
        this.outfile.write("]\n");
    }

    public void startKeyword(String name, String[] args) throws IOException {
        this.outfile.write("START KW: " + name + " [");
        for (int i=0; i < args.length; i++) {
            this.outfile.write(args[i]);
        }
        this.outfile.write("]\n");
    }

    public void endTest(String status, String message) throws IOException {
        if (status.equals("PASS")) {
            this.outfile.write("END TEST: " + status + "\n");
        }
        else {
            this.outfile.write("END TEST: " + status + ": " + message + "\n");
        }
    }

    public void endSuite(String stat, String msg) throws IOException {
        this.outfile.write("END SUITE: " + stat + ": " + msg + "\n");
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
