import java.util.*;


public class ArgumentTypes {

    public int handler_count = 41;

    /* Primitive types (8) */

    public void byte1(byte i) {
        System.out.println(i);
    }
    public void short1(short i) {
        System.out.println(i);
    }
    public void integer1(int i) {
        System.out.println(i);
    }
    public void long1(long i) {
        System.out.println(i);
    }
    public void float1(float f) {
        System.out.println(f);
    }
    public void double1(double d) {
        System.out.println(d);
    }
    public void boolean1(boolean b) {
        if (b)
            System.out.println("Oh Yes!!");
        else
            System.out.println("Oh No!!");
    }
    public void char1(char c) {
        System.out.println(c);
    }

    /* java.lang types (10) */

    public void byte2(Byte i) {
        System.out.println(i);
    }
    public void short2(Short i) {
        System.out.println(i);
    }
    public void integer2(Integer i) {
        System.out.println(i);
    }
    public void long2(Long i) {
        System.out.println(i);
    }
    public void float2(Float f) {
        System.out.println(f);
    }
    public void double2(Double d) {
        System.out.println(d);
    }
    public void boolean2(Boolean b) {
        if (b.booleanValue())
            System.out.println("Oh Yes!!");
        else
            System.out.println("Oh No!!");
    }
    public void char2(Character c) {
        System.out.println(c);
    }
    public void string(String s) {
        System.out.println(s);
    }
    public void object(Object o) {
        try {
            System.out.println(o.toString());
        }
        catch (NullPointerException n) {
            System.out.println("null");
        }
    }

    /* Primitive arrays (8) */

    public void byte1_array(byte[] ia) {
        for (int i=0; i<ia.length; i++) {
            this.byte1(ia[i]);
        }
    }
    public void short1_array(short[] ia) {
        for (int i=0; i<ia.length; i++) {
            this.short1(ia[i]);
        }
    }
    public void integer1_array(int[] ia) {
        for (int i=0; i<ia.length; i++) {
            this.integer1(ia[i]);
        }
    }
    public void long1_array(long[] ia) {
        for (int i=0; i<ia.length; i++) {
            this.long1(ia[i]);
        }
    }
    public void float1_array(float[] fa) {
        for (int i=0; i<fa.length; i++) {
            this.float1(fa[i]);
        }
    }
    public void double1_array(double[] da) {
        for (int i=0; i<da.length; i++) {
            this.double1(da[i]);
        }
    }
    public void boolean1_array(boolean[] ba) {
        for (int i=0; i<ba.length; i++) {
            this.boolean1(ba[i]);
        }
    }
    public void char1_array(char[] ca) {
        for (int i=0; i<ca.length; i++) {
            this.char1(ca[i]);
        }
    }

    /* java.lang arrays (10) */

    public void byte2_array(Byte[] ia) {
        for (int i=0; i<ia.length; i++) {
            this.byte2(ia[i]);
        }
    }
    public void short2_array(Short[] ia) {
        for (int i=0; i<ia.length; i++) {
            this.short2(ia[i]);
        }
    }
    public void integer2_array(Integer[] ia) {
        for (int i=0; i<ia.length; i++) {
            this.integer2(ia[i]);
        }
    }
    public void long2_array(Long[] ia) {
        for (int i=0; i<ia.length; i++) {
            this.long2(ia[i]);
        }
    }
    public void float2_array(Float[] fa) {
        for (int i=0; i<fa.length; i++) {
            this.float2(fa[i]);
        }
    }
    public void double2_array(Double[] da) {
        for (int i=0; i<da.length; i++) {
            this.double2(da[i]);
        }
    }
    public void boolean2_array(Boolean[] ba) {
        for (int i=0; i<ba.length; i++) {
            this.boolean2(ba[i]);
        }
    }
    public void char2_array(Character[] ca) {
        for (int i=0; i<ca.length; i++) {
            this.char2(ca[i]);
        }
    }
    public void string_array(String[] sa) {
        for (int i=0; i<sa.length; i++) {
            this.string(sa[i]);
        }
    }
    public void object_array(Object[] oa) {
        for (int i=0; i<oa.length; i++) {
            this.object(oa[i]);
        }
    }

    /* Lists (5) - No element type cast on coercion! */

    public void integer_list(List<Integer> il) {
        for (int i : il) {
            this.integer1(i);
        }
    }
    public void double_list(List<Double> dl) {
        for (double d : dl) {
            this.double1(d);
        }
    }
    public void boolean_list(List<Boolean> bl) {
        for (boolean b : bl) {
            this.boolean1(b);
        }
    }
    public void string_list(List<String> sl) {
        for (String s : sl) {
            this.string(s);
        }
    }
    public void object_list(List<Object> ol) {
        for (Object o : ol) {
            this.object(o);
        }
    }
}
