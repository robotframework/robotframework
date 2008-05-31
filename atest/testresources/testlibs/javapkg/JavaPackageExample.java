package javapkg;

import java.util.ArrayList;

public class JavaPackageExample {
	
	public void print(String msg) {
		System.out.println(msg);
	}
	
	public String returnValue() {
		return this.returnValue("Returned string value");
	}
	
	public String returnValue(String value) {
		return value;
	}

	public ArrayList returnArrayList() {
		ArrayList list = new ArrayList(3);
		list.add("one");
		list.add("two");
		list.add("three");
		return list;
	}
}