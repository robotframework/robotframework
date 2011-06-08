window.testdata = function () {

    var elementsById = {};
    var LEVEL = {I:'info', H:'info', T:'trace', W:'warn', E:'error', D:'debug', F:'fail'};
    var KEYWORD_TYPE = {kw: 'KEYWORD',
        setup:'SETUP',
        teardown:'TEARDOWN'};

    function addElement(elem) {
        elem.id = uuid();
        elementsById[elem.id] = elem;
        return elem;
    }

    function uuid() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function timestamp(millis) {
        return new Date(window.basemillis + millis);
    }

    // TODO: Remove this function and use texts.get everywhere.
    function get(id) {
        return texts.get(id)
    }

    function times(stats) {
        var start = timestamp(stats[1]);
        var elapsed = stats[2];
        var stop = timestamp(stats[1] + elapsed);
        return [start, stop, elapsed];
    }

    function message(element) {
        return addElement(
                model.Message(LEVEL[element[1]], timestamp(element[0]), get(element[2]), element[3]));
    }

    // TODO: Is separate status object needed? Probably not.
    function createStatus(stats, parentSuiteTeardownFailed) {
        var status = (stats[0] == "P" ? model.PASS : model.FAIL);
        return model.Status(status, parentSuiteTeardownFailed);
    }

    function last(items) {
        return items[items.length-1];
    }

    // TODO: Consider better name...
    function last2(items) {
        return items[items.length-2];
    }

    function childCreator(parent, childType) {
        return function (elem, index) {
            return addElement(childType(parent, elem, index));
        };
    }

    function createKeyword(parent, element, index) {
        var kw = model.Keyword({
            type: KEYWORD_TYPE[element[0]],
            name: get(element[1]),
            args: get(element[4]),
            doc: get(element[3]),
            status: createStatus(last(element)),
            times: model.Times(times(last(element))),
            parent: parent,
            index: index
        });
        kw.populateKeywords(Populator(element, keywordMatcher, childCreator(kw, createKeyword)));
        kw.populateMessages(Populator(element, messageMatcher, message));
        return kw;
    }

    var keywordMatcher = headerMatcher("kw", "setup", "teardown");

    function messageMatcher(elem) {
        return (elem.length == 3 &&
                typeof(elem[0]) == "number" &&
                typeof(elem[1]) == "string" &&
                typeof(elem[2]) == "number");
    }

    function tags(taglist) {
        return util.map(taglist, texts.get);
    }

    function createTest(suite, element) {
        var statusElement = last(element);
        var test = model.Test({
            parent: suite,
            name: get(element[1]),
            doc: get(element[4]),
            timeout: get(element[2]),
            isCritical: (element[3] == "Y"),
            status: createStatus(statusElement, suite.hasTeardownFailure()),
            message: createMessage(statusElement, suite.hasTeardownFailure()),
            times: model.Times(times(statusElement)),
            tags: tags(last2(element))
        });
        test.populateKeywords(Populator(element, keywordMatcher, childCreator(test, createKeyword)));
        return test;
    }

    function createMessage(statusElement, hasSuiteTeardownFailed) {
        var message = '';
        if (statusElement.length == 4)
            message = get(statusElement[3]);
        if(hasSuiteTeardownFailed)
            if(message === '')
                return 'Teardown of the parent suite failed.';
            else
                message += '\n\nAlso teardown of the parent suite failed.'
        return message;
    }

    function createSuite(parent, element) {
        var statusElement = last2(element);
        var suite = model.Suite({
            parent: parent,
            name: element[2],
            source: element[1],
            doc: get(element[3]),
            status: createStatus(statusElement, parent && parent.hasTeardownFailure()),
            message: createMessage(statusElement, parent && parent.hasTeardownFailure()),
            times: model.Times(times(statusElement)),
            statistics: suiteStats(last(element)),
            metadata: parseMetadata(element[4])
        });
        suite.populateKeywords(Populator(element, keywordMatcher, childCreator(suite, createKeyword)));
        suite.populateTests(Populator(element, headerMatcher("test"), childCreator(suite, createTest)));
        suite.populateSuites(Populator(element, headerMatcher("suite"), childCreator(suite, createSuite)));
        return suite;
    }

    function parseMetadata(data) {
        var metadata = {};
        for (var key in data) {
            metadata[key] = get(data[key]);
        }
        return metadata;
    }

    function suiteStats(stats) {
        return {
            total: stats[0],
            totalPassed: stats[1],
            totalFailed: stats[0] - stats[1],
            critical: stats[2],
            criticalPassed: stats[3],
            criticalFailed: stats[2] - stats[3]
        };
    }

    function headerMatcher() {
        var args = arguments;
        return function(elem) {
            for (var i = 0; i < args.length; i++)
                if (elem[0] == args[i]) return true;
            return false;
        };
    }

    function Populator(element, matcher, creator) {
        var items = findElements(element, matcher);
        return {
            numberOfItems: items.length,
            creator: function (index) {
                return creator(items[index], index);
            }
        };
    }

    function findElements(fromElement, matcher) {
        var results = new Array();
        for (var i = 0; i < fromElement.length; i++)
            if (matcher(fromElement[i]))
                results.push(fromElement[i]);
        return results;
    }

    function suite() {
        var elem = window.data[2];
        if (elementsById[elem.id])
            return elem;
        var main = addElement(createSuite(undefined, elem));
        window.data[2] = main;
        return main;
    }

    function findById(id) {
        return elementsById[id];
    }

    function pathToKeyword(fullname) {
        var root = suite();
        if (fullname.indexOf(root.fullname + ".") != 0) return [];
        return keywordPathTo(fullname + ".", root, [root.id]);
    }

    function pathToTest(fullname) {
        var root = suite();
        if (fullname.indexOf(root.fullname + ".") != 0) return [];
        return testPathTo(fullname, root, [root.id]);
    }

    function pathToSuite(fullname) {
        var root = suite();
        if (fullname.indexOf(root.fullname) != 0) return [];
        if (fullname == root.fullname) return [root.id];
        return suitePathTo(fullname, root, [root.id]);
    }

    function keywordPathTo(fullname, current, result) {
        if (fullname == "") return result;
        for (var i = 0; i < current.numberOfKeywords; i++) {
            var kw = current.keyword(i);
            if (fullname.indexOf(kw.path + ".") == 0) {
                result.push(kw.id);
                if (fullname == kw.path + ".")
                    return result;
                return keywordPathTo(fullname, kw, result);
            }
        }
        for (var i = 0; i < current.numberOfTests; i++) {
            var test = current.test(i);
            if (fullname.indexOf(test.fullname + ".") == 0) {
                result.push(test.id);
                return keywordPathTo(fullname, test, result);
            }
        }
        for (var i = 0; i < current.numberOfSuites; i++) {
            var suite = current.suite(i);
            if (fullname.indexOf(suite.fullname + ".") == 0) {
                result.push(suite.id);
                return keywordPathTo(fullname, suite, result);
            }
        }
    }

    function testPathTo(fullname, currentSuite, result) {
        for (var i = 0; i < currentSuite.numberOfTests; i++) {
            var test = currentSuite.test(i);
            if (fullname == test.fullname) {
                result.push(test.id);
                return result;
            }
        }
        for (var i = 0; i < currentSuite.numberOfSuites; i++) {
            var suite = currentSuite.suite(i);
            if (fullname.indexOf(suite.fullname + ".") == 0) {
                result.push(suite.id);
                return testPathTo(fullname, suite, result);
            }
        }
    }

    function suitePathTo(fullname, currentSuite, result) {
        for (var i = 0; i < currentSuite.numberOfSuites; i++) {
            var suite = currentSuite.suite(i);
            if (fullname == suite.fullname) {
                result.push(suite.id);
                return result;
            }
            if (fullname.indexOf(suite.fullname + ".") == 0) {
                result.push(suite.id);
                return suitePathTo(fullname, suite, result);
            }
        }
    }

    function generated() {
        return timestamp(window.data[0]);
    }

    function errors() {
        return util.map(window.data[4], message);
    }

    // TODO: Is this used anymore?
    function error(index) {
        return errors()[index];
    }

    function statistics() {
        var statData = window.data[3];
        return stats.Statistics(statData[0], statData[1], statData[2]);
    }

    return {
        suite: suite,
        errors: errors,
        error: error,
        find: findById,
        pathToTest: pathToTest,
        pathToSuite: pathToSuite,
        pathToKeyword: pathToKeyword,
        generated: generated,
        statistics: statistics
    };

}();

window.texts = (function () {

    function decode(text) {
        return (text[0] == '*' ? text.substring(1) : extract(text));
    }

    function extract(text) {
        var decoded = JXG.Util.Base64.decodeAsArray(text);
        var extracted = (new JXG.Util.Unzip(decoded)).unzip()[0][0];
        return JXG.Util.utf8Decode(extracted);
    }

    return {
        get: function (id) { return decode(window.strings[id]); }
    };

})();
