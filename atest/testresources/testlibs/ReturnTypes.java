public class ReturnTypes {

    public int handler_count = 9;

    public int return_integer() {
        return 2;
    }
    
    public double return_double() {
        return 3.14;
    }
    
    public boolean return_boolean() {
        return true;
    }
    
    public String return_string() {
    	return "Hello world";
    }
    
    public String return_null() {
    	return null;
    }

    public int[] return_int_array() {
    	return new int[] {1, 2, 3};
    }

    public void check_int_array(int[] ia) {
    	int[] expected = new int[] {1, 2, 3};
    	boolean success = true;
    	if ( ia.length != expected.length) {
    		success = false;
    	}
    	for (int i = 0; i < ia.length && success; i++) {
        	if (ia[i] != expected[i]) {
        		success = false;
        	}
    	} 
    	if (success == false) {
            throw new AssertionError();
    	}    	
    }

    public String[] return_string_array() {
    	return new String[] {"a", "b", "c"};
    }

    public void check_string_array(String[] sa) {
    	String[] expected = new String[] {"a", "b", "c"};
    	boolean success = true;
    	if ( sa.length != expected.length) {
    		success = false;
    	}
    	for (int i = 0; i < sa.length && success; i++) {
        	if (sa[i] != expected[i]) {
        		success = false;
        	}
    	} 
    	if (success == false) {
            throw new AssertionError();
    	}    	
    }    
}
