import java.util.*;

import org.python.core.*;


public class RunKeywordLibraryJavaWithKwargsSupport extends RunKeywordLibraryJava {

    public Object runKeyword(String name, PyTuple args, PyDictionary kwargs) {
        List<Object> superArgs = new ArrayList<Object>(Arrays.asList(args.toArray()));
        for (PyObject obj : kwargs.iteritems().asIterable()) {
            PyTuple item = (PyTuple)obj;
            superArgs.add(item.get(0).toString() + ":" + item.get(1).toString());
        }
        return super.runKeyword(name, superArgs.toArray());
    }
}
