window.output = {};

function multiplyString(string, times) {
    var result = "";
    for (var i = 0; i < times; i++){
        result += string;
    }
    return result;
}

describe("Text decoder", function () {

    it("should have empty string with id 0", function () {
        window.output.strings = ["*"];
        var empty = store.get(0);
        expect(empty).toEqual("");
    });

    it("should uncompress", function () {
        window.output.strings = ["*", "eNorzk3MySmmLQEASKop9Q=="];
        var decompressed = store.get(1);
        var expected = multiplyString("small", 20);
        expect(decompressed).toEqual(expected);
    });

    it("should uncompress and replace compressed in memory", function () {
        window.output.strings = ["*", "eNorzk3MySmmLQEASKop9Q=="];
        expect(window.output.strings[1]).toEqual("eNorzk3MySmmLQEASKop9Q==");
        store.get(1);
        var expected = multiplyString("small", 20);
        expect(window.output.strings[1]).toEqual("*"+expected);
    });

    it("should handle plain text", function () {
        window.output.strings = ["*", "*plain text"];
        var actual = store.get(1);
        expect(actual).toEqual("plain text");
    });
});


function populate(plainSuite, plainErrors) {
    var context = {strings: [], integers: []};
    var suite = convertListToIds(context, plainSuite);
    if (plainErrors == undefined)
        plainErrors = [];
    var errors = convertListToIds(context, plainErrors);
    window.output.generatedMillis = -41;
    window.output.baseMillis = 1000000000000;
    window.output.generator = "info";
    window.output.suite = suite;
    window.output.stats = [[["Critical Tests",0,1,"","",""],
                            ["All Tests",0,1,"","",""]],
                            [],
                            [["Tmp",0,1,"","Tmp",""],
                             ["Tmp.Test",0,1,"","Tmp.Test",""]]];
    window.output.strings = context.strings;
    window.output.integers = context.integers;
    window.output.errors = errors;
}

function convertListToIds(output, list) {
    var result = [];
    for (var key in list) {
        result[key] = addValue(output, list[key]);
    }
    return result;
}

function convertDictToIds(output, dict) {
    var result = {};
    for (var key in dict) {
        result[addValue(output, key)] = addValue(output, dict[key])
    }
    return result;
}

function addValue(output, value) {
        if (typeof(value) == 'number') {
            return addNumber(output.integers, value);
        } else if (typeof(value) == 'string') {
            return addString(output.strings, value);
        } else if (value instanceof Array) {
            return convertListToIds(output, value);
        } else {
            return convertDictToIds(output, value);
        }
}

function addNumber(integers, number) {
    var index = integers.indexOf(number);
    if (index == -1) {
        index = integers.length;
        integers[index] = number;
    }
    return -index - 1;
}

function addString(strings, text) {
    var index = strings.indexOf(text);
    if (index == -1) {
        index = strings.length;
        strings[index] = text;
    }
    return index;
}


function subSuite(index, suite) {
    if (!suite)
        suite = window.testdata.suite();
    return suite.suites()[index];
}

function firstTest(suite) {
    return suite.tests()[0];
}

function nthKeyword(item, n) {
    return item.keywords()[n];
}

describe("Handling Suite", function () {

    function getDate(offset) {
        return new Date(window.output.baseMillis + offset);
    }

    beforeEach(function () {
        var keyword = ["*kw","*lib.kw",'*',"*Kw doc.","*message", [0,"*I","*message"], ["*P",0,0]];
        var forloop = ["*forloop","*${i} IN RANGE [ 2 ]",'*','*','*',
            ["*foritem","*${i} = 0",'*','*','*', keyword, ["*P", 0, 0]], ["*P", 0, 0],
            ["*foritem","*${i} = 1",'*','*','*', keyword, ["*P", 0, 0]], ["*P", 0, 0]]
        var test = ["*test","*Test","*1 second","*Y", "*test doc", keyword, forloop, ["*tag1", "*tag2"],["*P",-1,2]];
        var suite = ["*suite","*/tmp/test.txt","*Suite","*suite doc",["*meta", "*data"], test, ["*P",-38,39], [1,1,1,1]];
        populate(suite);
    });

    function expectStats(suite, total, passed, critical, criticalPassed){
        expect(suite.total).toEqual(total);
        expect(suite.totalPassed).toEqual(passed);
        expect(suite.totalFailed).toEqual(total-passed);
        expect(suite.critical).toEqual(critical);
        expect(suite.criticalPassed).toEqual(criticalPassed);
        expect(suite.criticalFailed).toEqual(critical-criticalPassed);
    }

    it("should parse suite", function () {
        var suite = window.testdata.suite();
        expect(suite.name).toEqual("Suite");
        expect(suite.status).toEqual("PASS");
        expect(suite.source).toEqual("/tmp/test.txt");
        expect(suite.doc()).toEqual("suite doc");
        expect(suite.times).toBeDefined();
        expect(suite.times.elapsedMillis).toEqual(39);
        expectStats(suite, 1, 1, 1, 1);
        expect(suite.metadata[0]).toEqual(["meta", "data"]);
    });

    it("should parse test", function () {
        var test = firstTest(window.testdata.suite());
        expect(test.name).toEqual("Test");
        expect(test.status).toEqual("PASS");
        expect(test.fullName).toEqual("Suite.Test");
        expect(test.doc()).toEqual("test doc");
        expect(test.tags).toEqual(["tag1", "tag2"]);
        expect(test.times).toBeDefined();
        expect(test.times.elapsedMillis).toEqual(2);
        expect(test.timeout).toEqual("1 second");
    });

    it("should parse keyword", function () {
        var kw = nthKeyword(firstTest(window.testdata.suite()), 0);
        expect(kw.name).toEqual("lib.kw");
        expect(kw.status).toEqual("PASS");
        expect(kw.times).toBeDefined();
        expect(kw.times.elapsedMillis).toEqual(0);
        expect(kw.path).toEqual("Suite.Test.0");
        expect(kw.type).toEqual("KEYWORD");
    });

    it("should parse for loop", function() {
        var forloop = nthKeyword(firstTest(window.testdata.suite()), 1);
        expect(forloop.name).toEqual("${i} IN RANGE [ 2 ]");
        expect(forloop.type).toEqual("FOR");
        var foritem = nthKeyword(forloop, 0);
        expect(foritem.name).toEqual("${i} = 0");
        expect(foritem.type).toEqual("VAR");
        foritem = nthKeyword(forloop, 1);
        expect(foritem.name).toEqual("${i} = 1");
        expect(foritem.type).toEqual("VAR");
    });

    it("should parse message", function () {
        var message = nthKeyword(firstTest(window.testdata.suite()), 0).messages()[0];
        expect(message.text).toEqual("message");
    });

    it("should parse timestamp", function () {
        var timestamp = window.testdata.generated();
        expect(timestamp).toEqual(new Date(window.output.baseMillis-41));
    });

});

describe("Setups and teardowns", function () {

    beforeEach(function () {
        var suite =
            ["*suite","*/temp/suite.txt","*Suite",0,{},
                ["*setup","*Lib.Kw","*","*Blaa.","*sets",[0,"*I","*sets"],["*P",-1,1]],
                ["*test","*Test","*","*Y","*",
                    ["*setup","*Lib.Kw","*","*Blaa.","*sets",[1,"*I","*sets"],["*P",1,0]],["*kw","*Lib.Kw","*","*Blaa.","*sets",[2,"*I","*sets"],["*P",2,0]],
                    ["*teardown","*Lib.Kw","*","*Blaa.","*tears",[3,"*I","*tears"],["*P",3,0]],[],["*P",0,4]],
                ["*teardown","*Lib.Kw","*","*Blaa.","*tears",[4,"*I","*tears"],["*P",4,1]],["*P",-35,40],
                [1,1,1,1]];
        populate(suite);
    });

    function checkTypeNameArgs(kw, type, name, args) {
    	expect(kw.type).toEqual(type);
    	expect(kw.name).toEqual(name);
    	expect(kw.arguments).toEqual(args);
    }

    it("should parse suite setup", function () {
    	var suite = window.testdata.suite();
    	checkTypeNameArgs(suite.keywords()[0], "SETUP", "Lib.Kw", "sets");
    });

    it("should parse suite teardown", function () {
    	var suite = window.testdata.suite();
    	checkTypeNameArgs(suite.keywords()[1], "TEARDOWN", "Lib.Kw", "tears");
    });

    it("should give navigation uuid list for a suite teardown keyword", function (){
        var uuids = window.testdata.pathToKeyword("Suite.1");
        expect(uuids[0]).toEqual(window.testdata.suite().id);
        expect(uuids[1]).toEqual(nthKeyword(window.testdata.suite(), 1).id);
        expect(uuids.length).toEqual(2);
    });

    it("should parse test setup", function () {
        checkTypeNameArgs(nthKeyword(firstTest(window.testdata.suite()), 0), "SETUP", "Lib.Kw", "sets");
    });

    it("should parse test teardown", function () {
    	var test = firstTest(window.testdata.suite());
    	checkTypeNameArgs(nthKeyword(test, 2), "TEARDOWN", "Lib.Kw", "tears");
    });

    it("should give suite children in order", function () {
        var suite = window.testdata.suite();
        var children = suite.children();
        expect(children[0]).toEqual(nthKeyword(suite, 0));
        expect(children[1]).toEqual(nthKeyword(suite, 1));
        expect(children[2]).toEqual(firstTest(suite));
    });

    it("should give test children in order", function () {
        var test = firstTest(window.testdata.suite());
        var children = test.children();
        checkTypeNameArgs(children[0], "SETUP", "Lib.Kw", "sets");
        checkTypeNameArgs(children[1], "KEYWORD", "Lib.Kw", "sets");
        checkTypeNameArgs(children[2], "TEARDOWN", "Lib.Kw", "tears");
    });
});


describe("Short time formatting", function (){

    it("should pad 0 values to full length", function () {
        expect(window.model.shortTime(0,0,0,0)).toEqual("00:00:00.000");
    });

    it("should pad non empty number to full length", function () {
        expect(window.model.shortTime(12,5,55,101)).toEqual("12:05:55.101");
    });
});


describe("Handling messages", function (){

    beforeEach(function (){
        var suite =
            ["*suite","*/suite/verysimple.txt","*Verysimple","*",{},
                ["*test","*Test","*","*Y","*",
                    ["*kw","*Log","*","*Logging","*<h1>html</h1>, HTML",[0,"*H","*<h1>html</h1>"],["*P",0,0]],
                    ["*kw","*Log","*","*Logging","*infolevelmessage, INFO",[1,"*I","*infolevelmessage"],["*P",1,0]],
                    ["*kw","*Log","*","*Logging","*warning, WARN",[2,"*W","*warning"],["*P",2,0]],
                    ["*kw","*Log","*","*Logging","*debugging, DEBUG",[3,"*D","*debugging"],["*P",3,0]],
                    ["*kw","*Log","*","*Logging","*tracing, TRACE",[3,"*T","*tracing"],["*P",3,0]],
                    [],["*P",-1,4]],["*P",-28,32],[1,1,1,1]];
        var errors = [[2,"*W","*warning", "*keyword_Verysimple.Test.2"]];
        populate(suite, errors);
    });

    function expectMessage(message, txt, level) {
        expect(message.text).toEqual(txt);
        expect(message.level).toEqual(level);
    }

    function kwMessage(kw) {
        return nthKeyword(firstTest(window.testdata.suite()), kw).messages()[0];
    }

    it("should handle info level message", function () {
        expectMessage(kwMessage(1), "infolevelmessage", "info");
    });

    it("should handle warn level message", function () {
        expectMessage(kwMessage(2), "warning", "warn");
    });

    it("should handle debug level message", function () {
        expectMessage(kwMessage(3), "debugging", "debug");
    });

    it("should handle trace level message", function () {
        expectMessage(kwMessage(4), "tracing", "trace");
    });

    it("should handle html level message", function () {
        expectMessage(kwMessage(0), "<h1>html</h1>", "info");
    });

    it("should show warning in errors", function () {
        expectMessage(window.testdata.errors()[0], "warning", "warn");
        expect(window.testdata.errors()[0].link).toEqual("keyword_Verysimple.Test.2");
    });
});


describe("Parent Suite Teardown Failure", function (){
    beforeEach(function (){
        var suite =
            ["*suite","*/tmp","*Tmp","*",{},
                ["*suite","*/tmp/test.txt","*Test","*",{},
                    ["*test","*Testt","*","*Y","*",
                        ["*kw","*NoOp","*","*Does nothing.","*",["*P",0,1]],[],["*P",-1,2]],["*P",-2,3],
                    [1,0,1,0]],
                ["*teardown","*Fail","*","*Fails","*",[3,"*F","*AssertionError"],["*F",2,2]],
                ["*F",-37,41, "*Suite teardown failed:\nAssertionError"],[1,0,1,0]];
        populate(suite);
    });

    it("should show test status as failed", function (){
        var test = firstTest(window.testdata.suite().suites()[0]);
        expect(test.status).toEqual("FAIL");
    });

    it("should show suite status as failed", function (){
        var suite = window.testdata.suite().suites()[0];
        expect(suite.status).toEqual("FAIL");
    });

    it("should show test message 'Teardown of the parent suite failed.'", function (){
        var test = firstTest(window.testdata.suite().suites()[0]);
        expect(test.message()).toEqual("Teardown of the parent suite failed.");
    });

    it("should show suite message 'Teardown of the parent suite failed.'", function (){
        var suite = window.testdata.suite().suites()[0];
        expect(suite.message()).toEqual("Teardown of the parent suite failed.");
    });

    it("should show root suite message 'Suite teardown failed:\nAssertionError'", function (){
        var root = window.testdata.suite();
        expect(root.message()).toEqual("Suite teardown failed:\nAssertionError");
    });

});

describe("Parent Suite Teardown and Test failure", function(){
    beforeEach(function (){
        var suite =
            ["*suite","*/tmp/SuiteTeardown.txt","*SuiteTeardown","*",{},
                ["*test","*Failing","*","*Y","*",
                    ["*kw","*Fail","*","*Fails","*In test",[0,"*F","*In test"],["*F",-1,1]],[],
                    ["*F",-2,2,"*In test"]],
                ["*teardown","*Fail","*","*Fails","*in suite teardown",[1,"*F","*in suite teardown"],["*F",0,1]],
                ["*F",-23,24,"*Suite teardown failed:\nin suite teardown"],[1,0,1,0]];
        populate(suite);
    });

    it("should show test message 'In test\n\nAlso teardown of the parent suite failed.'", function (){
        var test = firstTest(window.testdata.suite());
        expect(test.message()).toEqual("In test\n\nAlso teardown of the parent suite failed.");
    });
})

describe("Test failure message", function (){

    beforeEach(function () {
        var suite =
            ["*suite","*/test.txt","*Test","*",{},
                ["*test","*Feilaava","*","*Y","*",
                    ["*kw","*feilaa","*","*","*",
                        ["*kw","*Fail","*","*Fails","*FooBar!",[0,"F","*FooBar!"],["*F",-1,1]],
                        ["*F",-1,1]],[],["*F",-2,3,"*FooBar!"]],
                ["*F",-29,30],[1,0,1,0]];
        populate(suite);
    });

    it("should show test failure message ''", function (){
        var test = firstTest(window.testdata.suite());
        expect(test.message()).toEqual("FooBar!");
    });
});

describe("Iterating Keywords", function (){

    beforeEach(function (){
        var suite =
            ["*suite","*/suite/verysimple.txt","*Verysimple","*",{},
                ["*test","*Test","*","*Y","*",
                    ["*kw","*kw1","*","*","*",["*kw","*Printtaa","*","*Logs things","*keyword1",[0,"*I","*keyword1"],["*P",-1,1]],["*P",-1,1]],
                    ["*kw","*kw2","*","*","*",["*kw","*Printtaa","*","*Logs things","*keyword2",[1,"*I","*keyword2"],["*P",1,0]],["*P",0,1]],
                    ["*kw","*kw3","*","*","*",["*kw","*Printtaa","*","*Logs things","*keyword3",[2,"*I","*keyword3"],["*P",2,1]],["*P",2,1]],
                    ["*kw","*kw4","*","*","*",["*kw","*Printtaa","*","*Logs things","*keyword4",[4,"*I","*keyword4"],["*P",4,0]],["*P",3,1]],
                    [],["*P",-2,7]],
                ["*P",-29,34], [1,1,1,1]];
        populate(suite);
    });

    function test(){
        return firstTest(window.testdata.suite());
    }

    function kw(index){
        return test().keyword(index);
    }

    it("should give correct number of keywords", function () {
        expect(test().keywords().length).toEqual(4);
        expect(nthKeyword(test(), 0).keywords().length).toEqual(1);
        expect(nthKeyword(nthKeyword(test(), 0), 0).keywords().length).toEqual(0);
    });

    it("should be possible to go through all the keywords in order", function () {
        var expectedKeywords = ["kw1", "kw2", "kw3", "kw4"];
        for(var i = 0; i < test().numberOfKeywords; i++){
            expect(kw(i).name).toEqual(expectedKeywords[i]);
        }
    });

    it("should give keyword children in order", function () {
        var keyword = nthKeyword(firstTest(window.testdata.suite()), 0);
        var children = keyword.children();
        expect(children[0]).toEqual(nthKeyword(keyword, 0));
    });
});


describe("Iterating Tests", function (){

    beforeEach(function (){
        var suite =
            ["*suite","*/verysimple.txt","*Verysimple","*",{},
                ["*test","*Test1","*","*Y","*",["*kw","*BuiltIn.Log","*","*Logs the given message with the given level.","*simple1",
                    [0,"*I","*simple1"],["*P",0,0]],[],["*P",-1,2]],
                ["*test","*Test2","*","*Y","*",["*kw","*BuiltIn.Log","*","*Logs the given message with the given level.","*simple2",
                    [2,"*I","*simple2"],["*P",2,0]],[],["*P",1,1]],
                ["*test","*Test3","*","*Y","*",["*kw","*BuiltIn.Log","*","*Logs the given message with the given level.","*simple3",
                    [3,"*I","*simple3"],["*P",3,0]],[],["*P",3,1]],
                ["*P",-28,32],[3,3,3,3]];
        populate(suite);
    });

    it("should give correct number of tests", function (){
        expect(window.testdata.suite().tests().length).toEqual(3);
    });

    it("should be possible to go through all the tests in order", function () {
        var expectedTests = ["Test1", "Test2", "Test3"];
        var tests = window.testdata.suite().tests();
        for(var i = 0; i <tests.length ; i++){
            expect(tests[i].name).toEqual(expectedTests[i]);
        }
    });
});


describe("Iterating Suites", function () {

    beforeEach(function (){
        var suite =
            ["*suite","*/foo","*Foo","*",{},
                ["*suite","*/foo/bar","*Bar","*",{},
                    ["*suite","*/foo/bar/testii.txt","*Testii","*",{},
                        ["*test","*FOO BAR","*","*Y","*",
                            ["*kw","*BuiltIn.Log","*","*Logs the given message with the given level.","*foo bar testi",[0,"*I","*foo bar testi"],["*P",-1,1]],[],["*P",-1,1]],
                        ["*P",-3,3],[1,1,1,1]],
                    ["*P",-4,5],[1,1,1,1]],
                ["*suite","*/foo/foo","*Foo","*",{},
                    ["*suite","*/foo/foo/tostii.txt","*Tostii","*",{},
                        ["*test","*FOO FOO","*","*Y","*",["*kw","*BuiltIn.No Operation","*","*Does absolutely nothing.","*",["*P",4,0]],[],
                            ["*P",4,1]],
                        ["*P",2,3],[1,1,1,1]],
                    ["*P",1,5],[1,1,1,1]],
                ["*P",-30,36],[2,2,2,2]];
        populate(suite);
    });

    it("should give correct number of suites", function (){
        var suite = window.testdata.suite();
        var subSuites = suite.suites();
        expect(subSuites.length).toEqual(2);
        expect(subSuites[0].suites().length).toEqual(1);
        expect(subSuites[1].suites()[0].suites().length).toEqual(0);
    });

    it("should be possible to iterate suites", function (){
        var tests = 0;
        var subSuites = window.testdata.suite().suites();
        for(var i = 0 in subSuites){
            for(var j in subSuites[i].suites()){
                var testsuite = subSuites[i].suites()[j];
                tests += testsuite.tests().length;
                expect(testsuite.tests().length).toEqual(1);
            }
        }
        expect(tests).toEqual(2);
    });

    it("should show correct full names", function (){
        var root = window.testdata.suite();
        expect(root.fullName).toEqual("Foo");
        expect(root.suites()[0].fullName).toEqual("Foo.Bar");
        expect(root.suites()[0].suites()[0].fullName).toEqual("Foo.Bar.Testii");
        expect(root.suites()[1].suites()[0].tests()[0].fullName).toEqual("Foo.Foo.Tostii.FOO FOO");
    });

    it("should give navigation uuid list for a test", function (){
        var uuidList = window.testdata.pathToTest("Foo.Foo.Tostii.FOO FOO");
        var root = window.testdata.suite();
        expect(uuidList[0]).toEqual(root.id);
        expect(uuidList[1]).toEqual(subSuite(1).id);
        expect(uuidList[2]).toEqual(subSuite(1).suites()[0].id);
        expect(uuidList[3]).toEqual(subSuite(1).suites()[0].tests()[0].id);
        expect(uuidList.length).toEqual(4);
    });

    it("should give navigation uuid list for a keyword", function (){
        var uuidList = window.testdata.pathToKeyword("Foo.Foo.Tostii.FOO FOO.0");
        var root = window.testdata.suite();
        expect(uuidList[0]).toEqual(root.id);
        expect(uuidList[1]).toEqual(subSuite(1).id);
        expect(uuidList[2]).toEqual(subSuite(1).suites()[0].id);
        expect(uuidList[3]).toEqual(subSuite(1).suites()[0].tests()[0].id);
        expect(uuidList[4]).toEqual(subSuite(1).suites()[0].tests()[0].keywords()[0].id);
        expect(uuidList.length).toEqual(5);
    });

    it("should give navigation uuid list for a suite", function (){
        var uuidList = window.testdata.pathToSuite("Foo.Bar.Testii");
        var root = window.testdata.suite();
        expect(uuidList[0]).toEqual(root.id);
        expect(uuidList[1]).toEqual(root.suites()[0].id);
        expect(uuidList[2]).toEqual(root.suites()[0].suites()[0].id);
        expect(uuidList.length).toEqual(3);
    });

    it("should give navigation uuid list for the root suite", function (){
        var uuidList = window.testdata.pathToSuite("Foo");
        var root = window.testdata.suite();
        expect(uuidList[0]).toEqual(root.id);
        expect(uuidList.length).toEqual(1);
    });

    it("should give empty navigation uuid list for unknown element", function (){
        var uuidList = window.testdata.pathToSuite("unknown");
        expect(uuidList).toEqual([]);
    });
});

describe("Element ids", function (){

    beforeEach(function (){
        var suite =
            ["*suite","*/foo","*Foo","*",{},
                ["*suite","*/foo/bar","*Bar","*",{},
                    ["*suite","*/foo/bar/testii.txt","*Testii","*",{},
                        ["*test","*FOO BAR","*","*Y","*",
                            ["*kw","*BuiltIn.Log","*","*Logs the given message with the given level.","*foo bar testi",[0,"*I","*foo bar testi"],["*P",-1,1]],[],["*P",-1,1]],
                        ["*P",-3,3],[1,1,1,1]],
                    ["*P",-4,5],[1,1,1,1]],
                ["*suite","*/foo/foo","*Foo","*",{},
                    ["*suite","*/foo/foo/tostii.txt","*Tostii","*",{},
                        ["*test","*FOO FOO","*","*Y","*",["*kw","*BuiltIn.No Operation","*","*Does absolutely nothing.","*",["*P",4,0]],[],
                            ["*P",4,1]],
                        ["*P",2,3],[1,1,1,1]],
                    ["*P",1,5],[1,1,1,1]],
                ["*P",-30,36],[2,2,2,2]];
        populate(suite);
    });

    it("should give id for the main suite", function (){
        var suite = window.testdata.suite();
        expect(window.testdata.find(suite.id)).toEqual(suite);
    });

    it("should give id for a test", function (){
        var test = subSuite(0, subSuite(0)).tests()[0];
        expect(window.testdata.find(test.id)).toEqual(test);
    });

    it("should give id for a subsuite", function (){
        var subsuite = subSuite(0);
        expect(window.testdata.find(subsuite.id)).toEqual(subsuite);
    });

    it("should give id for a keyword", function (){
        var kw = subSuite(0, subSuite(0)).tests()[0].keywords()[0];
        expect(window.testdata.find(kw.id)).toEqual(kw);
    });

    it("should give id for a message", function (){
        var msg = subSuite(0, subSuite(0)).tests()[0].keywords()[0].messages()[0];
        expect(window.testdata.find(msg.id)).toEqual(msg);
    });

    it("should find right elements with right ids", function (){
        var suite = subSuite(0);
        var kw = subSuite(0, suite).tests()[0].keywords()[0];
        expect(kw.id).not.toEqual(suite.id);
        expect(window.testdata.find(kw.id)).toEqual(kw);
        expect(window.testdata.find(suite.id)).toEqual(suite);
    });
});

describe("Elements are created only once", function (){

    beforeEach(function (){
        var suite =
            ["*suite","*/verysimple.txt","*Verysimple","*",{},
                ["*test","*Test1","*","*Y","*",["*kw","*BuiltIn.Log","*","*Logs the given message with the given level.","*simple1",[0,"*I","*simple1"],["*P",0,0]],[],
                    ["*P",-1,2]],
                ["*test","*Test2","*","*Y","*",["*kw","*BuiltIn.Log","*","*Logs the given message with the given level.","*simple2",[2,"*I","*simple2"],["*P",2,0]],[],
                    ["*P",1,1]],
                ["*test","*Test3","*","*Y","*",["*kw","*BuiltIn.Log","*","*Logs the given message with the given level.","*simple3",[3,"*I","*simple3"],["*P",3,0]],[],
                    ["*P",3,1]],
                ["*P",-28,32],[3,3,3,3]];
        populate(suite);
    });

    it("should create suite only once", function (){
        var main1 = window.testdata.suite();
        var main2 = window.testdata.suite();
        expect(main1).toEqual(main2);
    });

    it("should create same test only once", function (){
        var test1 = window.testdata.suite().tests()[2];
        var test2 = window.testdata.suite().tests()[2];
        expect(test1).toEqual(test2);
    });

    it("should create same keyword only once", function (){
        var kw1 = window.testdata.suite().tests()[0].keywords()[0];
        var kw2 = window.testdata.suite().tests()[0].keywords()[0];
        expect(kw1).toEqual(kw2);
    });
});

