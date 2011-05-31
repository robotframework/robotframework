window.testdata = (function(){

    var elementsById = {};
    var LEVEL = {I:'info', H:'info', T:'trace', W:'warn', E:'error', D:'debug', F:'fail'};
    var KEYWORD_TYPE = {kw: 'KEYWORD',
                        setup:'SETUP',
                        teardown:'TEARDOWN'};

    function addElement(elem){
        elem.id = uuid();
        elementsById[elem.id] = elem;
        return elem;
    }

    function uuid(){
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
            return v.toString(16);
        });
    }

    function timestamp(millis){
        return new Date(window.basemillis + millis);
    }

    function decode(text){
        return (text[0] == '*' ? text.substring(1) : extract(text));
    }

    function extract(text) {
        return JXG.Util.utf8Decode(
                (new JXG.Util.Unzip(JXG.Util.Base64.decodeAsArray(text))).unzip()[0][0]);
    }

    function get(id){
        return decode(window.strings[id]);
    }

    function times(stats){
        var start = timestamp(stats[1]);
        var elapsed = stats[2];
        var stop = timestamp(stats[1]+elapsed);
        return [start, stop, elapsed];
    }

    function message(element){
        return addElement(
                testmodel.Message(LEVEL[element[1]], timestamp(element[0]), get(element[2]), element[3]));
    }

    function status(stats){
        return (stats[0] == "P" ? testmodel.PASS : testmodel.FAIL);
    }

    function statuz(stats, parentSuiteTeardownFailed){
        return testmodel.Status(status(stats), parentSuiteTeardownFailed);
    }

    function last(items) {
        return items[items.length-1];
    }

    function childCreator(parent, childType) {
        return function (elem, index) { return addElement(childType(parent, elem, index)); };
    }

    function createKeyword(parent, element, index){
        var kw = testmodel.Keyword(
                KEYWORD_TYPE[element[0]],
                get(element[1]),
                get(element[4]),
                get(element[3]),
                statuz(last(element)),
                testmodel.Times(times(last(element))),
                parent,
                index);
        kw.populateKeywords(Populator(element, keywordMatcher, childCreator(kw, createKeyword)));
        kw.populateMessages(Populator(element, messageMatcher, message));
        return kw;
    }

    var keywordMatcher = headerMatcher("kw", "setup", "teardown");

    function messageMatcher(elem) {
        if(elem.length != 3) return false;
        if(typeof(elem[0]) != "number") return false;
        if(typeof(elem[1]) != "string") return false;
        if(typeof(elem[2]) != "number") return false;
        return true;
    }

    function tags(taglist){
        var tgs = [];
        for(var i in taglist) tgs[i] = get(taglist[i]);
        return tgs;
    }

    function createTest(suite, element) {
        var test = testmodel.Test(
                suite,
                get(element[1]),
                get(element[4]),
                get(element[2]),
                (element[3] == "Y"),
                statuz(last(element), suite.hasTeardownFailure()),
                testmodel.Times(times(last(element))),
                tags(element[element.length-2])
        );
        test.populateKeywords(Populator(element, keywordMatcher, childCreator(test, createKeyword)));
        return test;
    }

    function createSuite(parent, element) {
        var suit = testmodel.Suite(
                parent,
                element[2],
                element[1],
                get(element[3]),
                statuz(element[element.length-2], parent && parent.hasTeardownFailure()),
                testmodel.Times(times(element[element.length-2])),
                suiteStats(last(element)),
                parseMetadata(element[4])
        );
        suit.populateKeywords(Populator(element, keywordMatcher, childCreator(suit, createKeyword)));
        suit.populateTests(Populator(element, headerMatcher("test"), childCreator(suit, createTest)));
        suit.populateSuites(Populator(element, headerMatcher("suite"), childCreator(suit, createSuite)));
        return suit;
    }

    function parseMetadata(data){
        var metadata = {};
        for(var key in data){
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

    function headerMatcher(){
    	var args = arguments;
        return function(elem){
        		for (var i=0; i < args.length; i++)
        			if (elem[0] == args[i]) return true;
        		return false;
        		};
    }

    function Populator(element, matcher, creator) {
        var items = findElements(element, matcher);
        return {
            numberOfItems: items.length,
            creator: function (index) {return creator(items[index], index);}
        };
    }

    function findElements(fromElement, matcher) {
        var results = new Array();
        for(var i = 0; i < fromElement.length; i++)
            if(matcher(fromElement[i]))
                results.push(fromElement[i]);
        return results;
    }

    function suite() {
        var elem = window.data[2];
        if(elementsById[elem.id])
            return elem;
        var main = addElement(createSuite(undefined, elem));
        window.data[2] = main;
        return main;
    }

    function findById(id){
        return elementsById[id];
    }

    function pathToKeyword(fullname){
        var root = suite();
        if(fullname.indexOf(root.fullname+".") != 0) return [];
        return keywordPathTo(fullname+".", root, [root.id]);
    }

    function pathToTest(fullname){
        var root = suite();
        if(fullname.indexOf(root.fullname+".") != 0) return [];
        return testPathTo(fullname, root, [root.id]);
    }

    function pathToSuite(fullname){
        var root = suite();
        if(fullname.indexOf(root.fullname) != 0) return [];
        if(fullname == root.fullname) return [root.id];
        return suitePathTo(fullname, root, [root.id]);
    }

    function keywordPathTo(fullname, current, result){
        if(fullname == "") return result;
        for(var i = 0; i < current.numberOfKeywords; i++){
            var kw = current.keyword(i);
            if(fullname.indexOf(kw.path+".") == 0){
                result.push(kw.id);
                if(fullname == kw.path+".")
                    return result;
                return keywordPathTo(fullname, kw, result);
            }
        }
        for(var i = 0; i < current.numberOfTests; i++){
            var test = current.test(i);
            if(fullname.indexOf(test.fullname+".") == 0){
                result.push(test.id);
                return keywordPathTo(fullname, test, result);
            }
        }
        for(var i = 0; i < current.numberOfSuites; i++){
            var suite = current.suite(i);
            if(fullname.indexOf(suite.fullname+".") == 0){
                result.push(suite.id);
                return keywordPathTo(fullname, suite, result);
            }
        }
    }

    function testPathTo(fullname, currentSuite, result){
        for(var i = 0; i < currentSuite.numberOfTests; i++){
            var test = currentSuite.test(i);
            if(fullname == test.fullname){
                result.push(test.id);
                return result;
            }
        }
        for(var i = 0; i < currentSuite.numberOfSuites; i++){
            var suite = currentSuite.suite(i);
            if(fullname.indexOf(suite.fullname+".") == 0){
                result.push(suite.id);
                return testPathTo(fullname, suite, result);
            }
        }
    }

    function suitePathTo(fullname, currentSuite, result){
        for(var i = 0; i < currentSuite.numberOfSuites; i++){
            var suite = currentSuite.suite(i);
            if(fullname == suite.fullname){
                result.push(suite.id);
                return result;
            }
            if(fullname.indexOf(suite.fullname+".") == 0){
                result.push(suite.id);
                return suitePathTo(fullname, suite, result);
            }
        }
    }

    function padTo(number, len){
        var numString = number + "";
        while(numString.length < len) numString = "0"+numString;
        return numString;
    }

    function shortTime(hours, minutes, seconds, milliseconds){
        return padTo(hours, 2)+":"+padTo(minutes, 2)+":"+padTo(seconds, 2)+
                "."+padTo(milliseconds, 3);
    }

    function generated(){
        return timestamp(window.data[0]);
    }

    function error(index){
        if(window.data[4].length <= index)
            return undefined;
        return message(window.data[4][index]);
    }

    function stats(){
        var statdata = window.data[3];
        return {total: util.map(statdata[0], statElem),
                tag:   util.map(statdata[1], tagStatElem),
                suite: util.map(statdata[2], suiteStatElem)};
    }

    function statElem(data) {
        var stat = {
            label: data[0],
            pass:  data[1],
            fail:  data[2],
            total: data[1] + data[2],
            doc:   data[3]
        };
        var percents = calculatePercents(stat.total, stat.pass, stat.fail);
        stat.passPercent = percents[0];
        stat.failPercent = percents[1];
        var widths = calculateWidths(stat.passPercent, stat.failPercent);
        stat.passWidth = widths[0];
        stat.failWidth = widths[1];
        return stat;
    }

    function tagStatElem(data) {
        var stat = statElem(data);
        stat.info = data[4];
        if (stat.info)
            stat.shownInfo = '(' + stat.info + ')';
        else
            stat.shownInfo = '';
        stat.links = parseLinks(data[5]);
        return stat;
    }

    function suiteStatElem(data) {
        var stat = statElem(data);
        stat.fullname = function () { return stat.doc; };
        nameParts = stat.doc.split('.');
        stat.name = nameParts.pop();
        if (nameParts)
            nameParts.push('');
        stat.parentName = nameParts.join(' . ');
        return stat;
    }

    function parseLinks(linksData) {
        if (!linksData)
            return [];
        var items = linksData.split(':::');
        var links = [];
        for (var i=0; i<items.length; i++) {
            parts = items[i].split(':');
            links[i] = {title: parts[0], url: parts.splice(1).join(':')};
        }
        return links;
    }

    function calculatePercents(total, passed, failed) {
        if (total == 0)
            return [0.0, 0.0];
        pass = 100.0 * passed / total;
        fail = 100.0 * failed / total;
        if (pass > 0 && pass < 0.1)
            return [0.1, 99.9];
        if (fail > 0 && fail < 0.1)
            return [99.9, 0.1];
        return [Math.round(pass*10)/10, Math.round(fail*10)/10];
    }

    function calculateWidths(num1, num2) {
        if (num1 + num2 == 0)
            return [0.0, 0.0];
        // Make small percentages better visible
        if (num1 > 0 && num1 < 1)
            return [1.0, 99.0];
        if (num2 > 0 && num2 < 1)
            return [99.0, 1.0];
        // Handle situation where both are rounded up
        while (num1 + num2 > 100) {
            if (num1 > num2)
                num1 -= 0.1;
            if (num2 > num1)
                num2 -= 0.1;
        }
        return [num1, num2];
    }

    return {
        suite: suite,
        error: error,
        find: findById,
        pathToTest: pathToTest,
        pathToSuite: pathToSuite,
        pathToKeyword: pathToKeyword,
        generated: generated,
        getString: get,
        shortTime: shortTime,
        stats: stats
    };
}());

