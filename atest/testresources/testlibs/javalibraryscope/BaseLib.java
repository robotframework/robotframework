package javalibraryscope;

import java.util.HashMap;

public abstract class BaseLib {
	
	private HashMap registered;
	
	public BaseLib() {
		registered = new HashMap();
	}
	
	public void register(String name) {
		registered.put(name, null);
	}
	
	public void shouldBeRegistered(String[] expected) {
		HashMap exp = new HashMap();
		for (int i=0; i<expected.length; i++) {
			exp.put(expected[i], null);
		}
		if (! registered.equals(exp)) {	
			throw new AssertionError("Wrong registered: " + registered + " != " + exp);
		}
	}
}