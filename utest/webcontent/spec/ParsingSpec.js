window.output = {};

describe("Text decoder", function () {

    it("should have empty string with id 0", function () {
        window.output.strings = ["*"];
        var empty = texts.get(0);
        expect(empty).toEqual("");
    });

    it("should uncompress", function () {
        window.output.strings = ["*", "eNorzk3MySmmLQEASKop9Q=="];
        var decompressed = texts.get(1);
        var expected = "";
        for(var i = 0; i < 20; i++){
            expected += "small";
        }
        expect(decompressed).toEqual(expected);
    });

    it("should handle plain text", function () {
        window.output.strings = ["*", "*plain text"];
        var actual = texts.get(1);
        expect(actual).toEqual("plain text");
    });
});

function populateOutput(suite, strings, errors) {
    window.output.generatedMillis = -41;
    window.output.baseMillis = 1000000000000;
    window.output.generator = "info";
    window.output.suite = suite;
    window.output.stats = [[["Critical Tests",0,1,"","",""],
                            ["All Tests",0,1,"","",""]],
                            [],
                            [["Tmp",0,1,"","Tmp",""],
                             ["Tmp.Test",0,1,"","Tmp.Test",""]]];
    window.output.strings = strings;
    if (errors == undefined)
        errors = [];
    window.output.errors = errors;
}

describe("Handling Suite", function () {

    function getDate(offset) {
        return new Date(window.output.baseMillis + offset);
    }

    beforeEach(function () {
        var keyword = ["kw",2,0,3,4, [0,"I",4], ["P",0,0]];
        var test = ["test",1,10,"Y",6, keyword, [7, 8],["P",-1,2]];
        var suite = ["suite","/tmp/test.txt","Suite",5,{"meta":9}, test, ["P",-38,39], [1,1,1,1]];
        var strings = ["*","*Test","*lib.kw","*Kw doc.","*message",
                       "*suite doc", "*test doc", "*tag1", "*tag2",
                       "*data", "*1 second"];
        populateOutput(suite, strings);
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
        expect(suite.status).toEqual("pass");
        expect(suite.statusText).toEqual("PASS");
        expect(suite.source).toEqual("/tmp/test.txt");
        expect(suite.documentation).toEqual("suite doc");
        expect(suite.times).toBeDefined();
        expect(suite.times.elapsedMillis).toEqual(39);
        expectStats(suite, 1, 1, 1, 1);
        expect(suite.metadata["meta"]).toEqual("data");
    });

    it("should parse test", function () {
        var test = window.testdata.suite().test(0);
        expect(test.name).toEqual("Test");
        expect(test.status).toEqual("pass");
        expect(test.statusText).toEqual("PASS (critical)");
        expect(test.fullname).toEqual("Suite.Test");
        expect(test.documentation).toEqual("test doc");
        expect(test.tags).toEqual(["tag1", "tag2"]);
        expect(test.times).toBeDefined();
        expect(test.times.elapsedMillis).toEqual(2);
        expect(test.timeout).toEqual("1 second");
    });

    it("should parse keyword", function () {
        var kw = window.testdata.suite().test(0).keyword(0);
        expect(kw.name).toEqual("lib.kw");
        expect(kw.status).toEqual("pass");
        expect(kw.times).toBeDefined();
        expect(kw.times.elapsedMillis).toEqual(0);
        expect(kw.path).toEqual("Suite.Test.0");
    });

    it("should parse message", function () {
        var message = window.testdata.suite().test(0).keyword(0).message(0);
        expect(message.text).toEqual("message");
    });

    it("should parse timestamp", function () {
        var timestamp = window.testdata.generated();
        expect(timestamp).toEqual(new Date(window.output.baseMillis-41));
    });

});

describe("Setups and teardowns", function () {

    beforeEach(function () {
        var suite = ["suite","/temp/suite.txt","Suite",0,{},
                     ["setup",1,0,2,3,[0,"I",3],["P",-1,1]],
                     ["test",4,0,"Y",0,
                      ["setup",1,0,2,3,[1,"I",3],["P",1,0]],["kw",1,0,2,3,[2,"I",3],["P",2,0]],
                      ["teardown",1,0,2,5,[3,"I",5],["P",3,0]],[],["P",0,4]],
                     ["teardown",1,0,2,5,[4,"I",5],["P",4,1]],["P",-35,40],
                     [1,1,1,1]];
        var strings = ["*","*Lib.Kw","*Blaa.","*sets","*Test","*tears"];
        populateOutput(suite, strings);
    });

    function checkTypeNameArgs(kw, type, name, args) {
    	expect(kw.type).toEqual(type);
    	expect(kw.name).toEqual(name);
    	expect(kw.arguments).toEqual(args);
    }

    it("should parse suite setup", function () {
    	var suite = window.testdata.suite();
    	checkTypeNameArgs(suite.keyword(0), "SETUP", "Lib.Kw", "sets");
    });

    it("should parse suite teardown", function () {
    	var suite = window.testdata.suite();
    	checkTypeNameArgs(suite.keyword(1), "TEARDOWN", "Lib.Kw", "tears");
    });

    it("should give navigation uuid list for a suite teardown keyword", function (){
        var uuids = window.testdata.pathToKeyword("Suite.1");
        expect(uuids[0]).toEqual(window.testdata.suite().id);
        expect(uuids[1]).toEqual(window.testdata.suite().keyword(1).id);
        expect(uuids.length).toEqual(2);
    });

    it("should parse test setup", function () {
    	var test = window.testdata.suite().test(0);
    	checkTypeNameArgs(test.keyword(0), "SETUP", "Lib.Kw", "sets");
    });

    it("should parse test teardown", function () {
    	var test = window.testdata.suite().test(0);
    	checkTypeNameArgs(test.keyword(2), "TEARDOWN", "Lib.Kw", "tears");
    });

    it("should give suite children in order", function () {
        var suite = window.testdata.suite();
        var children = suite.children();
        expect(children[0]).toEqual(suite.keyword(0));
        expect(children[1]).toEqual(suite.keyword(1));
        expect(children[2]).toEqual(suite.test(0));
    });

    it("should give test children in order", function () {
        var test = window.testdata.suite().test(0);
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
        var suite = ["suite","/suite/verysimple.txt","Verysimple",0,{},
                     ["test",1,0,"Y",0,
                      ["kw",2,0,3,4,[0,"H",5],["P",0,0]],
                      ["kw",2,0,3,6,[1,"I",7],["P",1,0]],
                      ["kw",2,0,3,8,[2,"W",9],["P",2,0]],
                      ["kw",2,0,3,10,[3,"D",11],["P",3,0]],
                      ["kw",2,0,3,12,[3,"T",13],["P",3,0]],
                      [],["P",-1,4]],["P",-28,32],[1,1,1,1]];
        var strings = ["*","*Test","*Log","*Logging","*<h1>html</h1>, HTML",
                       "*<h1>html</h1>","*infolevelmessage, INFO",
                       "*infolevelmessage","*warning, WARN","*warning",
                       "*debugging, DEBUG","*debugging", "*tracing, TRACE",
                       "*tracing"];
        var errors = [[2,"W",9, "keyword_Verysimple.Test.2"]];
        populateOutput(suite, strings, errors);
    });

    function expectMessage(message, txt, level) {
        expect(message.text).toEqual(txt);
        expect(message.level).toEqual(level);
    }

    function kwMessage(kw) {
        return window.testdata.suite().test(0).keyword(kw).message(0);
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
        expectMessage(window.testdata.error(0), "warning", "warn");
        expect(window.testdata.error(0).link).toEqual("keyword_Verysimple.Test.2");
    });
});


describe("Parent Suite Teardown Failure", function (){
    beforeEach(function (){
        var suite = ["suite","/tmp","Tmp",0,{},
                     ["suite","/tmp/test.txt","Test",0,{},
                      ["test",1,0,"Y",0,
                       ["kw",2,0,3,0,["P",0,1]],[],["P",-1,2]],["P",-2,3],
                       [1,0,1,0]],
                       ["teardown",4,0,5,0,[3,"F",6],["F",2,2]],["F",-37,41, 7],[1,0,1,0]];
        var strings = ["*","*Testt","*NoOp","*Does nothing.",
                       "*Fail","*Fails","*AssertionError", "*Suite teardown failed:\nAssertionError"];
        populateOutput(suite, strings);
    });

    it("should show test status as failed", function (){
        var test = window.testdata.suite().suite(0).test(0);
        expect(test.status).toEqual("fail");
    });

    it("should show suite status as failed", function (){
        var suite = window.testdata.suite().suite(0);
        expect(suite.status).toEqual("fail");
    });

    it("should show test message 'Teardown of the parent suite failed.'", function (){
        var test = window.testdata.suite().suite(0).test(0);
        expect(test.message).toEqual("Teardown of the parent suite failed.");
    });

    it("should show suite message 'Teardown of the parent suite failed.'", function (){
        var suite = window.testdata.suite().suite(0);
        expect(suite.message).toEqual("Teardown of the parent suite failed.");
    });

    it("should show root suite message 'Suite teardown failed:\nAssertionError'", function (){
        var root = window.testdata.suite();
        expect(root.message).toEqual("Suite teardown failed:\nAssertionError");
    });

});

describe("Parent Suite Teardown and Test failure", function(){
    beforeEach(function (){
        var suite = ["suite","/tmp/SuiteTeardown.txt","SuiteTeardown",0,{},
                     ["test",1,0,"Y",0,
                      ["kw",2,0,3,4,[0,"F",4],["F",-1,1]],[],
                      ["F",-2,2,4]],
                      ["teardown",2,0,3,5,[1,"F",5],["F",0,1]],
                      ["F",-23,24,6],[1,0,1,0]];
        var strings = ["*","*Failing","*Fail","*Fails","*In test","*in suite teardown",
                       "*Suite teardown failed:\nin suite teardown"];
        populateOutput(suite, strings);
    });

    it("should show test message 'In test\n\nAlso teardown of the parent suite failed.'", function (){
        var test = window.testdata.suite().test(0);
        expect(test.message).toEqual("In test\n\nAlso teardown of the parent suite failed.");
    });
})

describe("Test failure message", function (){

    beforeEach(function () {
        var suite = ["suite","/test.txt","Test",0,{},
                     ["test",1,0,"Y",0,
                      ["kw",2,0,0,0,
                       ["kw",3,0,4,5,[0,"F",5],["F",-1,1]],
                       ["F",-1,1]],[],["F",-2,3,5]],
                       ["F",-29,30],[1,0,1,0]];
        var strings = ["*","*Feilaava","*feilaa","*Fail","*Fails","*FooBar!"];
        populateOutput(suite, strings);
    });

    it("should show test failure message ''", function (){
        var test = window.testdata.suite().test(0);
        expect(test.message).toEqual("FooBar!");
    });
});

describe("Iterating Keywords", function (){

    beforeEach(function (){
        var suite = ["suite","/suite/verysimple.txt","Verysimple",0,{},
                     ["test",1,0,"Y",0,
                      ["kw",2,0,0,0,["kw",3,0,4,5,[0,"I",5],["P",-1,1]],["P",-1,1]],
                      ["kw",6,0,0,0,["kw",3,0,4,7,[1,"I",7],["P",1,0]],["P",0,1]],
                      ["kw",8,0,0,0,["kw",3,0,4,9,[2,"I",9],["P",2,1]],["P",2,1]],
                      ["kw",10,0,0,0,["kw",3,0,4,11,[4,"I",11],["P",4,0]],
                       ["P",3,1]],[],["P",-2,7]],["P",-29,34], [1,1,1,1]];
        var strings = ["*","*Test","*kw1","*Printtaa","*Logs things",
                       "*keyword1","*kw2","*keyword2",
                       "*kw3","*keyword3","*kw4","*keyword4"];
        populateOutput(suite, strings);
    });

    function test(){
        return window.testdata.suite().test(0);
    }

    function kw(index){
        return test().keyword(index);
    }

    it("should give correct number of keywords", function () {
        expect(test().numberOfKeywords).toEqual(4);
        expect(test().keyword(0).numberOfKeywords).toEqual(1);
        expect(test().keyword(0).keyword(0).numberOfKeywords).toEqual(0);
    });

    it("should be possible to go through all the keywords in order", function () {
        var expectedKeywords = ["kw1", "kw2", "kw3", "kw4"];
        for(var i = 0; i < test().numberOfKeywords; i++){
            expect(kw(i).name).toEqual(expectedKeywords[i]);
        }
    });

    it("should give keyword children in order", function () {
        var keyword = window.testdata.suite().test(0).keyword(0);
        var children = keyword.children();
        expect(children[0]).toEqual(keyword.keyword(0));
    });
});


describe("Iterating Tests", function (){

    beforeEach(function (){
        var suite = ["suite","/verysimple.txt","Verysimple",0,{},
                     ["test",1,0,"Y",0,["kw",2,0,3,4,[0,"I",4],["P",0,0]],[],
                      ["P",-1,2]],
                      ["test",5,0,"Y",0,["kw",2,0,3,6,[2,"I",6],["P",2,0]],[],
                       ["P",1,1]],
                       ["test",7,0,"Y",0,["kw",2,0,3,8,[3,"I",8],["P",3,0]],[],
                        ["P",3,1]],
                        ["P",-28,32],[3,3,3,3]];
        var strings = ["*","*Test1","*BuiltIn.Log",
                       "*Logs the given message with the given level.",
                       "*simple1","*Test2","*simple2","*Test3","*simple3"];
        populateOutput(suite, strings);
    });

    it("should give correct number of tests", function (){
        expect(window.testdata.suite().numberOfTests).toEqual(3);
    });

    it("should be possible to go through all the tests in order", function () {
        var expectedTests = ["Test1", "Test2", "Test3"];
        var tests = window.testdata.suite().tests();
        for(var i = 0; i <tests.length ; i++){
            expect(tests[i].name).toEqual(expectedTests[i]);
        }
    });
});


describe("Iterating Suites", function (){

    beforeEach(function (){
        var suite = ["suite","/foo","Foo",0,{},
                     ["suite","/foo/bar","Bar",0,{},
                      ["suite","/foo/bar/testii.txt","Testii",0,{},
                       ["test",1,0,"Y",0,
                        ["kw",2,0,3,4,[0,"I",4],["P",-1,1]],[],["P",-1,1]],
                        ["P",-3,3],[1,1,1,1]],
                        ["P",-4,5],[1,1,1,1]],
                        ["suite","/foo/foo","Foo",0,{},
                         ["suite","/foo/foo/tostii.txt","Tostii",0,{},
                          ["test",5,0,"Y",0,["kw",6,0,7,0,["P",4,0]],[],
                           ["P",4,1]],
                           ["P",2,3],[1,1,1,1]],
                           ["P",1,5],[1,1,1,1]],
                           ["P",-30,36],[2,2,2,2]];
        var strings = ["*","*FOO BAR","*BuiltIn.Log",
                       "*Logs the given message with the given level.",
                       "*foo bar testi","*FOO FOO","*BuiltIn.No Operation",
                       "*Does absolutely nothing."];
        populateOutput(suite, strings);
    });

    it("should give correct number of suites", function (){
        var suite = window.testdata.suite();
        expect(suite.numberOfSuites).toEqual(2);
        expect(suite.suite(0).numberOfSuites).toEqual(1);
        expect(suite.suite(1).suite(0).numberOfSuites).toEqual(0);
    });

    it("should be possible to iterate suites", function (){
        var tests = 0;
        var subsuites = window.testdata.suite().suites();
        for(var i = 0; i < subsuites.length; i++){
            var subsuite = subsuites[i];
            for(var j = 0; j < subsuite.numberOfSuites; j++){
                var testsuite = subsuite.suite(j);
                tests += testsuite.numberOfTests;
                expect(testsuite.numberOfTests).toEqual(1);
            }
        }
        expect(tests).toEqual(2);
    });

    it("should show correct full names", function (){
        var root = window.testdata.suite();
        expect(root.fullname).toEqual("Foo");
        expect(root.suite(0).fullname).toEqual("Foo.Bar");
        expect(root.suite(0).suite(0).fullname).toEqual("Foo.Bar.Testii");
        expect(root.suite(1).suite(0).test(0).fullname).toEqual("Foo.Foo.Tostii.FOO FOO");
    });

    it("should give navigation uuid list for a test", function (){
        var uuidList = window.testdata.pathToTest("Foo.Foo.Tostii.FOO FOO");
        var root = window.testdata.suite();
        expect(uuidList[0]).toEqual(root.id);
        expect(uuidList[1]).toEqual(root.suite(1).id);
        expect(uuidList[2]).toEqual(root.suite(1).suite(0).id);
        expect(uuidList[3]).toEqual(root.suite(1).suite(0).test(0).id);
        expect(uuidList.length).toEqual(4);
    });

    it("should give navigation uuid list for a keyword", function (){
        var uuidList = window.testdata.pathToKeyword("Foo.Foo.Tostii.FOO FOO.0");
        var root = window.testdata.suite();
        expect(uuidList[0]).toEqual(root.id);
        expect(uuidList[1]).toEqual(root.suite(1).id);
        expect(uuidList[2]).toEqual(root.suite(1).suite(0).id);
        expect(uuidList[3]).toEqual(root.suite(1).suite(0).test(0).id);
        expect(uuidList[4]).toEqual(root.suite(1).suite(0).test(0).keyword(0).id);
        expect(uuidList.length).toEqual(5);
    });

    it("should give navigation uuid list for a suite", function (){
        var uuidList = window.testdata.pathToSuite("Foo.Bar.Testii");
        var root = window.testdata.suite();
        expect(uuidList[0]).toEqual(root.id);
        expect(uuidList[1]).toEqual(root.suite(0).id);
        expect(uuidList[2]).toEqual(root.suite(0).suite(0).id);
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
        var suite = ["suite","/foo","Foo",0,{},
                     ["suite","/foo/bar","Bar",0,{},
                      ["suite","/foo/bar/testii.txt","Testii",0,{},
                       ["test",1,0,"Y",0,
                        ["kw",2,0,3,4,[0,"I",4],["P",-1,1]],[],["P",-1,1]],
                        ["P",-3,3],[1,1,1,1]],
                        ["P",-4,5],[1,1,1,1]],
                        ["suite","/foo/foo","Foo",0,{},
                         ["suite","/foo/foo/tostii.txt","Tostii",0,{},
                          ["test",5,0,"Y",0,["kw",6,0,7,0,["P",4,0]],[],
                           ["P",4,1]],
                           ["P",2,3],[1,1,1,1]],
                           ["P",1,5],[1,1,1,1]],
                           ["P",-30,36],[2,2,2,2]];
        var strings = ["*","*FOO BAR","*BuiltIn.Log",
                       "*Logs the given message with the given level.",
                       "*foo bar testi","*FOO FOO","*BuiltIn.No Operation",
                       "*Does absolutely nothing."];
        populateOutput(suite, strings);
    });

    it("should give id for the main suite", function (){
        var suite = window.testdata.suite();
        expect(window.testdata.find(suite.id)).toEqual(suite);
    });

    it("should give id for a test", function (){
        var test = window.testdata.suite().suite(0).suite(0).test(0);
        expect(window.testdata.find(test.id)).toEqual(test);
    });

    it("should give id for a subsuite", function (){
        var subsuite = window.testdata.suite().suite(0);
        expect(window.testdata.find(subsuite.id)).toEqual(subsuite);
    });

    it("should give id for a keyword", function (){
        var kw = window.testdata.suite().suite(1).suite(0).test(0).keyword(0);
        expect(window.testdata.find(kw.id)).toEqual(kw);
    });

    it("should give id for a message", function (){
        var msg = window.testdata.suite().suite(0).
                  suite(0).test(0).keyword(0).message(0);
        expect(window.testdata.find(msg.id)).toEqual(msg);
    });

    it("should find right elements with right ids", function (){
        var suite = window.testdata.suite().suite(0);
        var kw = window.testdata.suite().suite(1).suite(0).test(0).keyword(0);
        expect(kw.id).not.toEqual(suite.id);
        expect(window.testdata.find(kw.id)).toEqual(kw);
        expect(window.testdata.find(suite.id)).toEqual(suite);
    });
});

describe("Elements are created only once", function (){

    beforeEach(function (){
        var suite = ["suite","/verysimple.txt","Verysimple",0,{},
                     ["test",1,0,"Y",0,["kw",2,0,3,4,[0,"I",4],["P",0,0]],[],
                      ["P",-1,2]],
                      ["test",5,0,"Y",0,["kw",2,0,3,6,[2,"I",6],["P",2,0]],[],
                       ["P",1,1]],
                       ["test",7,0,"Y",0,["kw",2,0,3,8,[3,"I",8],["P",3,0]],[],
                        ["P",3,1]],
                        ["P",-28,32],[3,3,3,3]];
        var strings = ["*","*Test1","*BuiltIn.Log",
                       "*Logs the given message with the given level.",
                       "*simple1","*Test2","*simple2","*Test3","*simple3"];
        populateOutput(suite, strings);
    });

    it("should create suite only once", function (){
        var main1 = window.testdata.suite();
        var main2 = window.testdata.suite();
        expect(main1).toEqual(main2);
    });

    it("should create same test only once", function (){
        var test1 = window.testdata.suite().test(2);
        var test2 = window.testdata.suite().test(2);
        expect(test1).toEqual(test2);
    });

    it("should create same keyword only once", function (){
        var kw1 = window.testdata.suite().test(0).keyword(0);
        var kw2 = window.testdata.suite().test(0).keyword(0);
        expect(kw1).toEqual(kw2);
    });
});

