window.testdata = function () {

    var elementsById = {};
    var idCounter = 0;
    var _statistics = null;
    var LEVELS = ['TRACE', 'DEBUG', 'INFO', 'WARN', 'FAIL', 'ERROR'];
    var STATUSES = ['FAIL', 'PASS', 'NOT_RUN'];
    var KEYWORDS = ['KEYWORD', 'SETUP', 'TEARDOWN', 'FOR', 'VAR'];

    function addElement(elem) {
        if (!elem.id)
            elem.id = uniqueId();
        elementsById[elem.id] = elem;
        return elem;
    }

    function uniqueId() {
        idCounter++;
        return 'element-id-' + idCounter;
    }

    function times(stats) {
        var startMillis = stats[1];
        var elapsed = stats[2];
        if (startMillis === null)
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

    function childCreator(parent, childType) {
        return function (elem, strings, index) {
            return addElement(childType(parent, elem, strings, index));
        };
    }

    function createKeyword(parent, element, strings, index) {
        var kw = model.Keyword({
            parent: parent,
            type: KEYWORDS[element[0]],
            id: 'k' + (index + 1),
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

    function createTest(parent, element, strings, index) {
        var statusElement = element[5];
        var test = model.Test({
            parent: parent,
            id: 't' + (index + 1),
            name: strings.get(element[0]),
            doc: function () {
                var doc = strings.get(element[3]);
                this.doc = function () { return doc; };
                return doc;
            },
            timeout: strings.get(element[1]),
            isCritical: element[2],
            status: parseStatus(statusElement),
            message: function () {
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
            id: 's' + ((index || 0) + 1),
            name: strings.get(element[0]),
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
            statistics: suiteStats(util.last(element)),
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
                               StringStore(window['strings'+structureIndex]),
                               index);
            }
        };
    }

    function suite() {
        var elem = window.output.suite;
        if (elementsById[elem.id])
            return elem;
        var root = addElement(createSuite(null, elem, StringStore(window.output.strings)));
        window.output.suite = root;
        return root;
    }

    function findLoaded(id) {
        return elementsById[id];
    }

    function ensureLoaded(id, callback) {
        var ids = id.split('-');
        var root = suite();
        ids.shift();
        loadItems(ids, root, [root.id], callback);
    }

    function loadItems(ids, current, result, callback) {
        if (!ids.length) {
            callback(result);
            return;
        }
        current.callWhenChildrenReady(function () {
            var id = ids.shift();
            var type = id[0];
            var index = parseInt(id.substring(1)) - 1;
            var item = selectFrom(current, type, index);
            result.push(item.id);
            loadItems(ids, item, result, callback);
        });
    }

    function selectFrom(element, type, index) {
        if (type === 'k') {
            return element.keywords()[index];
        } else if (type === 't') {
            return element.tests()[index];
        } else {
            return element.suites()[index];
        }
    }

    function errorIterator() {
        return {
            next: function () {
                return message(window.output.errors.shift(),
                               StringStore(window.output.strings));
            },
            hasNext: function () {
                return window.output.errors.length > 0;
            }
        };
    }

    function statistics() {
        if (!_statistics) {
            var statData = window.output.stats;
            _statistics = stats.Statistics(statData[0], statData[1], statData[2]);
        }
        return _statistics;
    }

    function StringStore(strings) {

        function getText(id) {
            var text = strings[id];
            if (!text)
                return '';
            if (text[0] == '*')
                return text.substring(1);
            var extracted = extract(text);
            strings[id] = '*' + extracted;
            return extracted;
        }

        function extract(text) {
            var decoded = JXG.Util.Base64.decodeAsArray(text);
            var extracted = (new JXG.Util.Unzip(decoded)).unzip()[0][0];
            return JXG.Util.UTF8.decode(extracted);
        }

        function get(id) {
            if (id === null) return null;
            return getText(id);
        }

        return {get: get};
    }

    return {
        suite: suite,
        errorIterator: errorIterator,
        findLoaded: findLoaded,
        ensureLoaded: ensureLoaded,
        statistics: statistics,
        StringStore: StringStore,  // exposed for tests
        LEVELS: LEVELS
    };

}();
