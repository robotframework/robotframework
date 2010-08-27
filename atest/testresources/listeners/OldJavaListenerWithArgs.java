import java.io.*;


public class OldJavaListenerWithArgs {
	
	public OldJavaListenerWithArgs(String arg1, String arg2) throws IOException {
		String tmpdir = JavaTempDir.getTempDir();
		String sep = System.getProperty("file.separator");
		String outpath = tmpdir + sep + "java_listener_with_args.txt";
		BufferedWriter outfile = new BufferedWriter(new FileWriter(outpath));
		outfile.write("I got arguments '" + arg1 + "' and '" + arg2 + "'\n");
		outfile.close();
	}
}
