describe("Text decoder", function () {

    function multiplyString(string, times) {
        var result = "";
        for (var i = 0; i < times; i++){
            result += string;
        }
        return result;
    }

    it("should have empty string with id 0", function () {
        var strings = window.testdata.StringStore(["*"]);
        var empty = strings.get(0);
        expect(empty).toEqual("");
    });

    it("should uncompress", function () {
        var strings = window.testdata.StringStore(["*", "eNorzk3MySmmLQEASKop9Q=="]);
        var decompressed = strings.get(1);
        var expected = multiplyString("small", 20);
        expect(decompressed).toEqual(expected);
    });

    it("should uncompress and replace compressed in memory", function () {
        var stringArray = ["*", "eNorzk3MySmmLQEASKop9Q=="];
        var strings = window.testdata.StringStore(stringArray);
        expect(stringArray[1]).toEqual("eNorzk3MySmmLQEASKop9Q==");
        strings.get(1);
        var expected = multiplyString("small", 20);
        expect(stringArray[1]).toEqual("*"+expected);
    });

    it("should handle plain text", function () {
        var strings = window.testdata.StringStore(["*", "*plain text"]);
        var actual = strings.get(1);
        expect(actual).toEqual("plain text");
    });
});

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
        window.output = window.suiteOutput;
    });

    function expectStats(suite, total, passed, failed, skipped){
        expect(suite.total).toEqual(total);
        expect(suite.pass).toEqual(passed);
        expect(suite.fail).toEqual(failed);
        expect(suite.skip).toEqual(skipped);
    }

    function endsWith(string, ending) {
        var index = string.lastIndexOf(ending);
        return string.substring(index) == ending;
    }

    it("should parse suite", function () {
        var suite = window.testdata.suite();
        expect(suite.name).toEqual("Suite");
        expect(suite.id).toEqual("s1");
        expect(suite.status).toEqual("PASS");
        expect(endsWith(suite.source, "Suite.robot")).toEqual(true);
        expect(suite.doc()).toEqual("<p>suite doc</p>");
        expect(suite.times).toBeDefined();
        expect(suite.times.elapsedMillis).toBeGreaterThan(0);
        expect(suite.times.elapsedMillis).toBeLessThan(1000);
        expectStats(suite, 1, 1, 0, 0);
        expect(suite.metadata[0]).toEqual(["meta", "<p>data</p>"]);
        expect(suite.childrenNames).toEqual(['keyword', 'suite', 'test']);
    });

    it("should parse test", function () {
        var test = firstTest(window.testdata.suite());
        expect(test.name).toEqual("Test");
        expect(test.id).toEqual("s1-t1");
        expect(test.status).toEqual("PASS");
        expect(test.fullName).toEqual("Suite.Test");
        expect(test.doc()).toEqual("<p>test doc</p>");
        expect(test.tags).toEqual(["tag1", "tag2"]);
        expect(test.times).toBeDefined();
        expect(test.times.elapsedMillis).toBeGreaterThan(0);
        expect(test.times.elapsedMillis).toBeLessThan(window.testdata.suite().times.elapsedMillis+1);
        expect(test.timeout).toEqual("1 second");
        expect(test.childrenNames).toEqual(['keyword']);
    });

    it("should parse keyword", function () {
        var kw = nthKeyword(firstTest(window.testdata.suite()), 0);
        expect(kw.name).toEqual("Sleep");
        expect(kw.libname).toEqual("BuiltIn");
        expect(kw.id).toEqual("s1-t1-k1");
        expect(kw.status).toEqual("PASS");
        expect(kw.times).toBeDefined();
        expect(kw.times.elapsedMillis).toBeGreaterThan(99);
        expect(kw.times.elapsedMillis).toBeLessThan(200);
        expect(kw.type).toEqual("KEYWORD");
        expect(kw.childrenNames).toEqual(['keyword']);
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
        var message = nthKeyword(firstTest(window.testdata.suite()), 0).children()[0];
        expect(message.text).toEqual("Slept 100 milliseconds");
    });

});

describe("Setups and teardowns", function () {

    beforeEach(function () {
        window.output = window.setupsAndTeardownsOutput;
    });

    function checkTypeNameArgs(kw, type, name, libname, args) {
        expect(kw.type).toEqual(type);
        expect(kw.name).toEqual(name);
        expect(kw.libname).toEqual(libname);
        expect(kw.arguments).toEqual(args);
    }

    it("should parse suite setup", function () {
        var suite = window.testdata.suite();
        checkTypeNameArgs(suite.keywords()[0], "SETUP", "Log", "BuiltIn", "suite setup");
    });

    it("should parse suite teardown", function () {
        var suite = window.testdata.suite();
        checkTypeNameArgs(suite.keywords()[1], "TEARDOWN", "Log", "BuiltIn", "suite teardown");
    });

    it("should give navigation uniqueId list for a suite teardown keyword", function () {
        var callbackExecuted = false;
        window.testdata.ensureLoaded("s1-k2", function (uniqueIds) {
            expect(uniqueIds[0]).toEqual(window.testdata.suite().id);
            expect(uniqueIds[1]).toEqual(nthKeyword(window.testdata.suite(), 1).id);
            expect(uniqueIds.length).toEqual(2);
            callbackExecuted = true;
        });
        expect(callbackExecuted).toBeTruthy();
    });

    it("should parse test setup", function () {
        checkTypeNameArgs(nthKeyword(firstTest(window.testdata.suite()), 0), "SETUP", "Log", "BuiltIn", "test setup");
    });

    it("should parse test teardown", function () {
        var test = firstTest(window.testdata.suite());
        checkTypeNameArgs(nthKeyword(test, 2), "TEARDOWN", "Log", "BuiltIn", "test teardown");
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
        checkTypeNameArgs(children[0], "SETUP", "Log", "BuiltIn", "test setup");
        checkTypeNameArgs(children[1], "KEYWORD", "Keyword with teardown", "", "");
        checkTypeNameArgs(children[2], "TEARDOWN", "Log", "BuiltIn", "test teardown");
    });

    it("should parse keyword teardown", function () {
        var test = firstTest(window.testdata.suite());
        var children = test.children();
        checkTypeNameArgs(children[1].children()[1], "TEARDOWN", "Log", "BuiltIn", "keyword teardown");
    });
});


describe("Time and date formatting", function (){

    it("should pad 0 values to full length", function () {
        expect(util.dateTimeFromDate(new Date(2011,7-1,1,0,0,0,0))).toEqual("20110701 00:00:00.000");
        expect(util.dateFromDate(new Date(2011,7-1,1,0,0,0,0))).toEqual("20110701");
        expect(util.timeFromDate(new Date(2011,7-1,1,0,0,0,0))).toEqual("00:00:00.000");
    });

    it("should pad non empty number to full length", function () {
        expect(util.dateTimeFromDate(new Date(2011,7-1,14,12,5,55,101))).toEqual("20110714 12:05:55.101");
    });
});


describe("Handling messages", function (){

    beforeEach(function (){
        window.output = window.messagesOutput;
    });

    function expectMessage(message, txt, level) {
        expect(message.text).toEqual(txt);
        expect(message.level).toEqual(level);
    }

    function kwMessages(kw) {
        return nthKeyword(firstTest(window.testdata.suite()), kw).children();
    }

    function kwMessage(kw) {
        return kwMessages(kw)[0];
    }

    it("should handle info level message", function () {
        expectMessage(kwMessage(1), "infolevelmessage", "INFO");
    });

    it("should handle warn level message", function () {
        expectMessage(kwMessage(2), "warning", "WARN");
    });

    it("should handle debug level message", function () {
        var messages = kwMessages(4);
        expectMessage(messages[messages.length-2], "debugging", "DEBUG");
    });

    it("should handle trace level message", function () {
        var messages = kwMessages(5);
        expectMessage(messages[messages.length-2], "tracing", "TRACE");
    });

    it("should handle html level message", function () {
        expectMessage(kwMessage(0), "<h1>html</h1>", "INFO");
    });

    it("should show warning in errors", function () {
        var firstError = window.testdata.errorIterator().next();
        expectMessage(firstError, "warning", "WARN");
        var callbackExecuted = false;
        window.testdata.ensureLoaded(firstError.link, function (pathToKeyword) {
            var errorKw = window.testdata.findLoaded(pathToKeyword[pathToKeyword.length-1]);
            expect(errorKw.children()[0].level).toEqual("WARN");
            callbackExecuted = true;
        });
        expect(callbackExecuted).toBeTruthy();
    });

    it("should handle fail level message", function () {
        expectMessage(kwMessage(7), "HTML tagged content <a href='http://www.robotframework.org'>Robot Framework</a>", "FAIL");
    });
});


describe("Parent Suite Teardown Failure", function (){
    beforeEach(function (){
        window.output = window.teardownFailureOutput;
    });

    it("should show test status as failed", function (){
        var test = firstTest(window.testdata.suite().suites()[0]);
        expect(test.status).toEqual("FAIL");
    });

    it("should show suite status as failed", function (){
        var suite = window.testdata.suite().suites()[0];
        expect(suite.status).toEqual("FAIL");
    });

    it("should show test message 'Parent suite teardown failed.'", function (){
        var test = firstTest(window.testdata.suite().suites()[0]);
        expect(test.message()).toEqual("Parent suite teardown failed:\nAssertionError");
    });

    it("should not show suite message", function (){
        var suite = window.testdata.suite().suites()[0];
        expect(suite.message()).toEqual("");
    });

    it("should show root suite message 'Suite teardown failed:\nAssertionError'", function (){
        var root = window.testdata.suite();
        expect(root.message()).toEqual("Suite teardown failed:\nAssertionError");
    });

});

describe("Parent Suite Teardown and Test failure", function(){
    beforeEach(function (){
        window.output = window.teardownFailureOutput;
    });

    it("should show test message 'In test\n\nAlso parent suite teardown failed.'", function (){
        var test = window.testdata.suite().suites()[0].tests()[1];
        expect(test.message()).toEqual("In test\n\nAlso parent suite teardown failed:\nAssertionError");
    });
})

describe("Test failure message", function (){

    beforeEach(function () {
        window.output = window.passingFailingOutput;
    });

    it("should show test failure message ''", function (){
        var test = window.testdata.suite().tests()[1];
        expect(test.message()).toEqual("In test");
    });
});

describe("Iterating Keywords", function (){

    beforeEach(function (){
        window.output = window.testsAndKeywordsOutput;
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
        window.output = window.testsAndKeywordsOutput;
    });

    it("should give correct number of tests", function (){
        expect(window.testdata.suite().tests().length).toEqual(4);
    });

    it("should be possible to go through all the tests in order", function () {
        var expectedTests = ["Test 1", "Test 2", "Test 3", "Test 4"];
        var tests = window.testdata.suite().tests();
        for(var i = 0; i <tests.length ; i++){
            expect(tests[i].name).toEqual(expectedTests[i]);
        }
    });
});


describe("Iterating Suites", function () {

    beforeEach(function (){
        window.output = window.allDataOutput;
    });

    it("should give correct number of suites", function (){
        var suite = window.testdata.suite();
        var subSuites = suite.suites();
        expect(subSuites.length).toEqual(5);
        expect(subSuites[0].suites().length).toEqual(0);
        expect(subSuites[3].suites().length).toEqual(1);
    });

    it("should be possible to iterate suites", function (){
        var tests = 0;
        var subSuites = window.testdata.suite().suites();
        for(var i = 0 in subSuites){
            for(var j in subSuites[i].suites()){
                var testsuite = subSuites[i].suites()[j];
                tests += testsuite.tests().length;
                expect(testsuite.tests().length).toBeGreaterThan(0);
            }
        }
        expect(tests).toEqual(2);
    });

    it("should show correct full names", function (){
        var root = window.testdata.suite();
        expect(root.fullName).toEqual("Data");
        expect(root.suites()[0].fullName).toEqual("Data.Messages");
        expect(root.suites()[3].suites()[0].fullName).toEqual("Data.teardownFailure.PassingFailing");
        expect(root.suites()[3].suites()[0].tests()[0].fullName).toEqual("Data.teardownFailure.PassingFailing.Passing");
    });

    function testensureLoaded(path, callback) {
        var callbackExecuted = false;
        window.testdata.ensureLoaded(path, function (ids) {
            callback(ids);
            callbackExecuted = true;
        });
        expect(callbackExecuted).toBeTruthy();
    }

    it("should give navigation uniqueId list for a test", function (){
        testensureLoaded("s1-s4-s1-t1", function (uniqueIdList) {
            var root = window.testdata.suite();
            expect(uniqueIdList[0]).toEqual(root.id);
            expect(uniqueIdList[1]).toEqual(subSuite(3).id);
            expect(uniqueIdList[2]).toEqual(subSuite(3).suites()[0].id);
            expect(uniqueIdList[3]).toEqual(subSuite(3).suites()[0].tests()[0].id);
            expect(uniqueIdList.length).toEqual(4);
        });
    });

    it("should give navigation uniqueId list for a keyword", function (){
        testensureLoaded("s1-s4-s1-t1-k1", function (uniqueIdList) {
            var root = window.testdata.suite();
            expect(uniqueIdList[0]).toEqual(root.id);
            expect(uniqueIdList[1]).toEqual(subSuite(3).id);
            expect(uniqueIdList[2]).toEqual(subSuite(3).suites()[0].id);
            expect(uniqueIdList[3]).toEqual(subSuite(3).suites()[0].tests()[0].id);
            expect(uniqueIdList[4]).toEqual(subSuite(3).suites()[0].tests()[0].keywords()[0].id);
            expect(uniqueIdList.length).toEqual(5);
        });
    });

    it("should give navigation uniqueId list for a suite", function (){
        testensureLoaded("s1-s4-s1", function (uniqueIdList) {
            var root = window.testdata.suite();
            expect(uniqueIdList[0]).toEqual(root.id);
            expect(uniqueIdList[1]).toEqual(root.suites()[3].id);
            expect(uniqueIdList[2]).toEqual(root.suites()[3].suites()[0].id);
            expect(uniqueIdList.length).toEqual(3);
        });
    });

    it("should give navigation uniqueId list for the root suite", function (){
        testensureLoaded("s1", function (uniqueIdList) {
            var root = window.testdata.suite();
            expect(uniqueIdList[0]).toEqual(root.id);
            expect(uniqueIdList.length).toEqual(1);
        });
    });
});

describe("Element ids", function (){

    beforeEach(function (){
        window.output = window.allDataOutput;
    });

    it("should give id for the main suite", function (){
        var suite = window.testdata.suite();
        expect(window.testdata.findLoaded(suite.id)).toEqual(suite);
        expect(suite.id).toEqual("s1");
    });

    it("should give id for a test", function (){
        var test = subSuite(0, subSuite(3)).tests()[0];
        expect(window.testdata.findLoaded(test.id)).toEqual(test);
        expect(test.id).toEqual("s1-s4-s1-t1");
    });

    it("should give id for a subsuite", function (){
        var subsuite = subSuite(3);
        expect(window.testdata.findLoaded(subsuite.id)).toEqual(subsuite);
        expect(subsuite.id).toEqual("s1-s4");
    });

    it("should give id for a keyword", function (){
        var kw = subSuite(0, subSuite(3)).tests()[0].keywords()[0];
        expect(window.testdata.findLoaded(kw.id)).toEqual(kw);
        expect(kw.id).toEqual("s1-s4-s1-t1-k1");
    });

    it("should give id for a message", function (){
        var msg = subSuite(0, subSuite(3)).tests()[0].keywords()[0].children()[0];
        expect(window.testdata.findLoaded(msg.id)).toEqual(msg);
    });

    it("should find right elements with right ids", function (){
        var suite = subSuite(3);
        var kw = subSuite(0, suite).tests()[0].keywords()[0];
        expect(kw.id).not.toEqual(suite.id);
        expect(window.testdata.findLoaded(kw.id)).toEqual(kw);
        expect(window.testdata.findLoaded(suite.id)).toEqual(suite);
    });
});

describe("Elements are created only once", function (){

    beforeEach(function (){
        window.output = window.passingFailingOutput;
    });

    it("should create suite only once", function (){
        var main1 = window.testdata.suite();
        var main2 = window.testdata.suite();
        expect(main1).not.toBeUndefined();
        expect(main1).toEqual(main2);
    });

    it("should create same test only once", function (){
        var test1 = window.testdata.suite().tests()[1];
        var test2 = window.testdata.suite().tests()[1];
        expect(test1).not.toBeUndefined();
        expect(test1).toEqual(test2);
    });

    it("should create same keyword only once", function (){
        var kw1 = window.testdata.suite().tests()[0].keywords()[0];
        var kw2 = window.testdata.suite().tests()[0].keywords()[0];
        expect(kw1).not.toBeUndefined();
        expect(kw1).toEqual(kw2);
    });
});

describe("Should split tests and keywords with --splitlog", function (){

    beforeEach(function (){
        window.output = window.splittingOutput;
        var i = 1;
        while (window['splittingOutputKeywords'+i]) {
            window['keywords'+i] = window['splittingOutputKeywords'+i];
            window['strings'+i] = window['splittingOutputStrings'+i];
            i = i+1;
        }
        var originalGetter = window.fileLoading.getCallbackHandlerForKeywords;
        window.fileLoading.getCallbackHandlerForKeywords = function(parent) {
            var normalResult = originalGetter(parent);
            function wrapper(callable) {
                parent.isChildrenLoaded = true;
                normalResult(callable);
            }
            return wrapper;
        }
    });

    it("should not load children before needed", function (){
        var suite = window.testdata.suite();
        var test = firstTest(subSuite(1, suite));
        expect(test.isChildrenLoaded).not.toBeTruthy();
        expect(test.children()).toBeUndefined();
        test.callWhenChildrenReady(function() {});
        expect(test.isChildrenLoaded).toBeTruthy();
        expect(test.children()).not.toBeUndefined();
    });

});
