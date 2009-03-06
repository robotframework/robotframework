import org.python.core.*;

public class LoginApplication extends java.lang.Object implements org.python.core.PyProxy, org.python.core.ClassDictInit {
    static String[] jpy$mainProperties = new String[] {"python.modules.builtin", "exceptions:org.python.core.exceptions"};
    static String[] jpy$proxyProperties = new String[] {"python.modules.builtin", "exceptions:org.python.core.exceptions", "python.options.showJavaExceptions", "true"};
    static String[] jpy$packages = new String[] {"java.lang", null};
    
    public static class _PyInner extends PyFunctionTable implements PyRunnable {
        private static PyObject s$0;
        private static PyObject s$1;
        private static PyFunctionTable funcTable;
        private static PyCode c$0_start;
        private static PyCode c$1_LoginApplication;
        private static PyCode c$2_main;
        private static void initConstants() {
            s$0 = Py.newString("__main__");
            s$1 = Py.newString("/home/jth/workspace/proto/lib/LoginApplication.py");
            funcTable = new _PyInner();
            c$0_start = Py.newCode(1, new String[] {"self"}, "/home/jth/workspace/proto/lib/LoginApplication.py", "start", false, false, funcTable, 0, null, null, 0, 17);
            c$1_LoginApplication = Py.newCode(0, new String[] {}, "/home/jth/workspace/proto/lib/LoginApplication.py", "LoginApplication", false, false, funcTable, 1, null, null, 0, 16);
            c$2_main = Py.newCode(0, new String[] {}, "/home/jth/workspace/proto/lib/LoginApplication.py", "main", false, false, funcTable, 2, null, null, 0, 16);
        }
        
        
        public PyCode getMain() {
            if (c$2_main == null) _PyInner.initConstants();
            return c$2_main;
        }
        
        public PyObject call_function(int index, PyFrame frame) {
            switch (index){
                case 0:
                return _PyInner.start$1(frame);
                case 1:
                return _PyInner.LoginApplication$2(frame);
                case 2:
                return _PyInner.main$3(frame);
                default:
                return null;
            }
        }
        
        private static PyObject start$1(PyFrame frame) {
            frame.getglobal("MainFrame").__call__().invoke("show");
            return Py.None;
        }
        
        private static PyObject LoginApplication$2(PyFrame frame) {
            frame.setlocal("start", new PyFunction(frame.f_globals, new PyObject[] {}, c$0_start));
            return frame.getf_locals();
        }
        
        private static PyObject main$3(PyFrame frame) {
            frame.setglobal("__file__", s$1);
            
            // Temporary Variables
            PyObject[] t$0$PyObject__;
            
            // Code
            frame.setlocal("java", org.python.core.imp.importOne("java.lang.Object", frame));
            t$0$PyObject__ = org.python.core.imp.importFrom("application", new String[] {"MainFrame"}, frame);
            frame.setlocal("MainFrame", t$0$PyObject__[0]);
            t$0$PyObject__ = null;
            frame.setlocal("LoginApplication", Py.makeClass("LoginApplication", new PyObject[] {frame.getname("java").__getattr__("lang").__getattr__("Object")}, c$1_LoginApplication, null, LoginApplication.class));
            if (frame.getname("__name__")._eq(s$0).__nonzero__()) {
                frame.getname("LoginApplication").__call__().invoke("start");
            }
            return Py.None;
        }
        
    }
    public static void moduleDictInit(PyObject dict) {
        dict.__setitem__("__name__", new PyString("LoginApplication"));
        Py.runCode(new _PyInner().getMain(), dict, dict);
    }
    
    public static void main(String[] args) throws java.lang.Exception {
        String[] newargs = new String[args.length+1];
        newargs[0] = "LoginApplication";
        java.lang.System.arraycopy(args, 0, newargs, 1, args.length);
        Py.runMain(LoginApplication._PyInner.class, newargs, LoginApplication.jpy$packages, LoginApplication.jpy$mainProperties, null, new String[] {"LoginApplication"});
    }
    
    public java.lang.Object clone() throws java.lang.CloneNotSupportedException {
        return super.clone();
    }
    
    public void finalize() throws java.lang.Throwable {
        super.finalize();
    }
    
    public LoginApplication() {
        super();
        __initProxy__(new Object[] {});
    }
    
    private PyInstance __proxy;
    public void _setPyInstance(PyInstance inst) {
        __proxy = inst;
    }
    
    public PyInstance _getPyInstance() {
        return __proxy;
    }
    
    private PySystemState __sysstate;
    public void _setPySystemState(PySystemState inst) {
        __sysstate = inst;
    }
    
    public PySystemState _getPySystemState() {
        return __sysstate;
    }
    
    public void __initProxy__(Object[] args) {
        Py.initProxy(this, "LoginApplication", "LoginApplication", args, LoginApplication.jpy$packages, LoginApplication.jpy$proxyProperties, null, new String[] {"LoginApplication"});
    }
    
    static public void classDictInit(PyObject dict) {
        dict.__setitem__("__supernames__", Py.java2py(new String[] {"finalize", "clone"}));
    }
    
}
