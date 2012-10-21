window.testdata = function () {

    var elementsById = {};
    var idCounter = 0;
    var _statistics = null;
    var LEVELS = ['TRACE', 'DEBUG', 'INFO', 'WARN', 'FAIL', 'ERROR'];
    var STATUSES = ['FAIL', 'PASS', 'NOT_RUN'];
    var KEYWORDS = ['KEYWORD', 'SETUP', 'TEARDOWN', 'FOR', 'VAR'];

    function addElement(elem) {
        if (elem.id == undefined)
            elem.id = uniqueId();
        elementsById[elem.id] = elem;
        return elem;
    }

    function uniqueId() {
        idCounter++;
        return "elementId_" + idCounter;
    }

    function times(stats) {
        var startMillis = stats[1];
        var elapsed = stats[2];
        if (startMillis == null)
            return [null, null, elapsed];
        return [util.timestamp(startMillis),
                util.timestamp(startMillis + elapsed),
                elapsed];
    }

    function message(element, strings) {
        return addElement(model.Message(LEVELS[element[1]],
                                        util.timestamp(element[0]),
                                        strings.get(element[2]),
                                        strings.get(element[3])));
    }

    function parseStatus(stats) {
        return STATUSES[stats[0]];
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
            type: KEYWORDS[element[0]],
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
            index: index,
            isChildrenLoaded: typeof(element[6]) !== 'number'
        });
        lazyPopulateKeywordsFromFile(kw, element[6], strings);
        kw.populateMessages(Populator(element[7], strings, message));
        return kw;
    }

    function lazyPopulateKeywordsFromFile(parent, keywordsOrIndex, strings) {
        if (parent.isChildrenLoaded) {
            var keywords = keywordsOrIndex;
            parent.populateKeywords(Populator(keywords, strings, childCreator(parent, createKeyword)));
        } else {
            var index = keywordsOrIndex;
            parent.childFileName = window.settings['splitLogBase'] + '-' + index + '.js';
            parent.populateKeywords(SplitLogPopulator(keywordsOrIndex, childCreator(parent, createKeyword)));
        }
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
            isCritical: element[2],
            status: parseStatus(statusElement),
            message:  function () {
                var msg = createMessage(statusElement, strings);
                this.message = function () { return msg; };
                return msg;
            },
            times: model.Times(times(statusElement)),
            tags: tags(element[4], strings),
            isChildrenLoaded: typeof(element[6]) !== 'number'
        });
        lazyPopulateKeywordsFromFile(test, element[6], strings);
        return test;
    }

    function createMessage(statusElement, strings) {
        return statusElement.length == 4 ? strings.get(statusElement[3]) : '';
    }

    function createSuite(parent, element, strings, index) {
        var statusElement = element[5];
        var suite = model.Suite({
            parent: parent,
            name: strings.get(element[0]),
            index: index,
            source: strings.get(element[1]),
            relativeSource: strings.get(element[2]),
            doc: function () {
                var doc = strings.get(element[3]);
                this.doc = function () { return doc; };
                return doc;
            },
            status: parseStatus(statusElement),
            message: function () {
                var msg = createMessage(statusElement, strings);
                this.message = function () { return msg; };
                return msg;
            },
            times: model.Times(times(statusElement)),
            statistics: suiteStats(last(element)),
            metadata: parseMetadata(element[4], strings)
        });
        suite.populateKeywords(Populator(element[8], strings, childCreator(suite, createKeyword)));
        suite.populateTests(Populator(element[7], strings, childCreator(suite, createTest)));
        suite.populateSuites(Populator(element[6], strings, childCreator(suite, createSuite)));
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
        if (ids[0] != "s1") {
            return;
        }
        var root = suite();
        ids.shift();
        findPathWithId(ids, root, [root.id], callback);
    }

    function findPathWithId(pathId, current, result, callback) {
        if (pathId.length == 0) {
            callback(result);
        } else {
            current.callWhenChildrenReady(function () {
                doWithSelected(current, pathId[0][0], parseInt(pathId[0].substring(1))-1, function (item) {
                result.push(item.id);
                pathId.shift();
                findPathWithId(pathId, item, result, callback);
            })});
        }
    }

    function doWithSelected(element, selector, index, func) {
        var item = selectFrom(element, selector, index);
        if (item !== undefined) {
           func(item);
        }
    }

    function selectFrom(element, selector, index) {
        if (selector == "k") {
            return element.keywords()[index];
        } else if(selector == "t") {
            return element.tests()[index];
        } else if(selector == "s") {
            return element.suites()[index];
        }
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
        statistics: statistics,
        getStringStore: getStringStore,
        LEVELS: LEVELS
    };

}();
