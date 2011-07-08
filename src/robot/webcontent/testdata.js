window.testdata = function () {

    var elementsById = {};
    var idCounter = 0;
    var _statistics = null;
    var LEVELS = {T: 'trace', D: 'debug', I: 'info', H: 'info',
                  W: 'warn', E: 'error', F: 'fail'};
    var KEYWORD_TYPE = {kw: 'KEYWORD', setup: 'SETUP', teardown: 'TEARDOWN',
                        forloop: 'FOR', foritem: 'VAR'};

    function addElement(elem) {
        if(elem.id == undefined)
            elem.id = uniqueId();
        elementsById[elem.id] = elem;
        return elem;
    }

    function uniqueId() {
        idCounter++;
        return "elementId_" + idCounter;
    }

    function timestamp(millis) {
        return new Date(window.output.baseMillis + millis);
    }

    function times(stats) {
        var startMillis = stats[1];
        var elapsed = stats[2];
        if (startMillis == null)
            return [null, null, elapsed];
        return [timestamp(startMillis), timestamp(startMillis + elapsed), elapsed];
    }

    function message(element, strings) {
        return addElement(model.Message(LEVELS[strings.get(element[1])],
                                        timestamp(element[0]),
                                        strings.get(element[2]),
                                        strings.get(element[3])));
    }

    function parseStatus(stats, strings, parentSuiteTeardownFailed) {
        if (parentSuiteTeardownFailed)
            return model.FAIL;
        return {'P': model.PASS,
                'F': model.FAIL,
                'N': model.NOT_RUN}[strings.get(stats[0])];
    }

    function last(items) {
        return items[items.length-1];
    }

    function childCreator(parent, childType) {
        return function (elem, strings, index) {
            return addElement(childType(parent, elem, strings, index));
        };
    }

    function createKeyword(parent, element, strings, index) {
        var kw = model.Keyword({
            type: KEYWORD_TYPE[strings.get(element[0])],
            name: strings.get(element[1]),
            timeout: strings.get(element[2]),
            args: strings.get(element[4]),
            doc: function () {
                var doc = strings.get(element[3]);
                this.doc = function () { return doc; };
                return doc;
            },
            status: parseStatus(element[5], strings),
            times: model.Times(times(element[5])),
            parent: parent,
            index: index
        });
        kw.populateKeywords(Populator(element[6], strings, childCreator(kw, createKeyword)));
        kw.populateMessages(Populator(element[7], strings, message));
        return kw;
    }

    function tags(taglist, strings) {
        return util.map(taglist, strings.get);
    }

    function createTest(suite, element, strings, index) {
        var statusElement = element[5];
        var test = model.Test({
            parent: suite,
            name: strings.get(element[0]),
            index: index,
            doc: function () {
                var doc = strings.get(element[3]);
                this.doc = function () { return doc; };
                return doc;
            },
            timeout: strings.get(element[1]),
            isCritical: (strings.get(element[2]) == "Y"),
            status: parseStatus(statusElement, strings, suite.hasTeardownFailure()),
            message:  function () {
                var msg = createMessage(statusElement, strings, suite.hasTeardownFailure());
                this.message = function () { return msg; };
                return msg;
            },
            times: model.Times(times(statusElement)),
            tags: tags(element[4], strings),
            isChildrenLoaded: typeof(element[6]) !== 'number'
        });
        if (test.isChildrenLoaded) {
            test.populateKeywords(Populator(element[6], strings, childCreator(test, createKeyword)));
        } else {
            test.childFileName = window.settings['logURL'].replace('.html', '-'+element[6]+'.js');
            test.populateKeywords(SplitLogPopulator(element[6], childCreator(test, createKeyword)));
        }
        return test;
    }

    function createMessage(statusElement, strings, hasSuiteTeardownFailed) {
        var message = statusElement.length == 4 ? strings.get(statusElement[3]) : '';
        if (!hasSuiteTeardownFailed)
            return message;
        if (message)
            return message + '\n\nAlso teardown of the parent suite failed.';
        return 'Teardown of the parent suite failed.';
    }

    function createSuite(parent, element, strings, index) {
        var statusElement = element[4];
        var suite = model.Suite({
            parent: parent,
            name: strings.get(element[1]),
            index: index,
            source: strings.get(element[0]),
            doc: function () {
                var doc = strings.get(element[2]);
                this.doc = function () { return doc; };
                return doc;
            },
            status: parseStatus(statusElement, strings, parent && parent.hasTeardownFailure()),
            parentSuiteTeardownFailed: parent && parent.hasTeardownFailure(),
            message: function () {
                var msg = createMessage(statusElement, strings, parent && parent.hasTeardownFailure());
                this.message = function () { return msg; };
                return msg;
            },
            times: model.Times(times(statusElement)),
            statistics: suiteStats(last(element)),
            metadata: parseMetadata(element[3], strings)
        });
        suite.populateKeywords(Populator(element[7], strings, childCreator(suite, createKeyword)));
        suite.populateTests(Populator(element[6], strings, childCreator(suite, createTest)));
        suite.populateSuites(Populator(element[5], strings, childCreator(suite, createSuite)));
        return suite;
    }

    function parseMetadata(data, strings) {
        var metadata = [];
        for (var i=0; i<data.length; i+=2) {
            metadata.push([strings.get(data[i]), strings.get(data[i+1])]);
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

    function Populator(items, strings, creator) {
        return {
            numberOfItems: function () {
                return items.length;
            },
            creator: function (index) {
                return creator(items[index], strings, index);
            }
        };
    }

    function SplitLogPopulator(structureIndex, creator) {
        return {
            numberOfItems: function () {
                return window['keywords'+structureIndex].length;
            },
            creator: function (index) {
                return creator(window['keywords'+structureIndex][index],
                               getStringStore(window['strings'+structureIndex]),
                               index);
            }
        };
    }

    function suite() {
        var elem = window.output.suite;
        if (elementsById[elem.id])
            return elem;
        var main = addElement(createSuite(undefined, elem, getStringStore(window.output.strings)));
        window.output.suite = main;
        return main;
    }

    function findById(id) {
        return elementsById[id];
    }

    function findPathTo(pathId, callback) {
        var ids = pathId.split("-");
        if(ids[0] != "s1"){
            callback([]);
            return;
        }
        var root = suite();
        ids.shift();
        findPathWithId(ids, root, [root.id], callback);
    }

    function findPathWithId(pathId, current, result, callback) {
        if(pathId.length == 0){
            callback(result);
        } else {
            current.callWhenChildrenReady(function () {
                var item = selectFrom(current, pathId[0][0], parseInt(pathId[0].substring(1))-1);
                result.push(item.id);
                pathId.shift();
                findPathWithId(pathId, item, result, callback);
            });
        }
    }

    function selectFrom(element, selector, index) {
        if(selector == "k"){
            return element.keywords()[index];
        } else if(selector == "t") {
            return element.tests()[index];
        } else if(selector == "s") {
            return element.suites()[index];
        }
    }

    function generated() {
        return timestamp(window.output.generatedMillis);
    }

    function errors() {
        var iterator = new Object();
        iterator.counter = 0;
        iterator.next = function () {
            return message(window.output.errors[iterator.counter++],
                           getStringStore(window.output.strings));
        };
        iterator.hasNext = function () {
            return iterator.counter < window.output.errors.length;
        };
        return iterator;
    }

    function statistics() {
        if (!_statistics) {
            var statData = window.output.stats;
            _statistics = stats.Statistics(statData[0], statData[1], statData[2]);
        }
        return _statistics;
    }

    function getStringStore(strings) {

        function getText(id) {
            var text = strings[id];
            if (!text)
                return '';
            if (text[0] == '*')
                return text.substring(1);
            var extracted = extract(text);
            strings[id] = "*"+extracted;
            return extracted;
        }

        function extract(text) {
            var decoded = JXG.Util.Base64.decodeAsArray(text);
            var extracted = (new JXG.Util.Unzip(decoded)).unzip()[0][0];
            return JXG.Util.utf8Decode(extracted);
        }

        function get(id) {
            if (id == undefined) return undefined;
            if (id == null) return null;
            return getText(id);
        }

        return {get: get};
    }

    return {
        suite: suite,
        errors: errors,
        find: findById,
        findPathTo: findPathTo,
        generated: generated,
        statistics: statistics,
        getStringStore: getStringStore
    };

}();
