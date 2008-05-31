public class ArgumentsJava {
    
    public String a_0() {
        return "a_0";
    }
    
    public String a_1(String arg) {
        return "a_1: " + arg;
    }
    
    public String a_3(String arg1, String arg2, String arg3) {
        return "a_3: " + arg1 + " " + arg2 + " " + arg3;
    }	
    
    public String a_0_1() {
        return a_0_1("default");
    }
    
    public String a_0_1(String arg) {
        return "a_0_1: " + arg;
    }

    public String a_1_3(String arg1) {
    	return a_1_3(arg1, "default");
    }
    
    public String a_1_3(String arg1, String arg2) {
    	return a_1_3(arg1, arg2, "default");
    }

    public String a_1_3(String arg1, String arg2, String arg3) {
        return "a_1_3: " + arg1 + " " + arg2 + " " + arg3;
    }
    
    public String a_0_n(String[] args) {
    	String ret = "a_0_n:";
    	for (int i=0; i < args.length; i++) {
    		ret += " " + args[i];
    	}
    	return ret;
    }

    public String a_1_n(String arg, String[] args) {
    	String ret = "a_1_n: " + arg;
    	for (int i=0; i < args.length; i++) {
    		ret += " " + args[i];
    	}
    	return ret;
    }
    
}