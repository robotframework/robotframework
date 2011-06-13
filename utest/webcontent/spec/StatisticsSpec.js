describe("Statistics", function () {

    beforeEach(function () {
        window.data =
            [undefined,undefined,undefined,
             [[["Critical Tests", 1,1,"","", ""],
               ["All Tests", 2,3,"","", ""]],
              [["first tag", 3, 0, "tagdoc", "critical", "title:url:::t2:u2"],
               ["second tag", 1, 0, "", "", ""]],
              [["Suite", 4, 0, "Suite", "", ""],
               ["Suite.Sub", 4, 0, "Suite.Sub", "", ""]]],
             undefined];
    });

    function verifyBasicStatAttributes(stat, label, pass, fail, doc) {
        expect(stat.label).toEqual(label);
        expect(stat.pass).toEqual(pass);
        expect(stat.fail).toEqual(fail);
        expect(stat.total).toEqual(pass+fail);
        expect(stat.doc).toEqual(doc);
    }

    function verifySuiteStatNames(stat, name, parentName) {
        expect(stat.name).toEqual(name);
        expect(stat.parentName).toEqual(parentName);
    }

    it("should contain critical stats", function () {
        var criticalstats = window.testdata.statistics().total[0];
        verifyBasicStatAttributes(criticalstats, 'Critical Tests', 1, 1, '');
    });

    it("should contain all stats", function () {
        var allstats = window.testdata.statistics().total[1];
        verifyBasicStatAttributes(allstats, 'All Tests', 2, 3, '');
    });

    it("should contain tag statistics", function () {
        var tagstats = window.testdata.statistics().tag;
        var firstTagStats = tagstats[0];
        verifyBasicStatAttributes(firstTagStats, 'first tag', 3, 0, 'tagdoc');
        expect(firstTagStats.shownInfo).toEqual('(critical)');
        var secondTagStats = tagstats[1];
        verifyBasicStatAttributes(secondTagStats, 'second tag', 1, 0, '');
        expect(secondTagStats.shownInfo).toEqual('');
    });

    it("should contain tag stat links", function () {
        var tagWithLink = window.testdata.statistics().tag[0];
        expect(tagWithLink.links).toEqual([{title: "title", url: "url"},
                                           {title: "t2", url: "u2"}]);
        var tagWithNoLink = window.testdata.statistics().tag[1];
        expect(tagWithNoLink.links).toEqual([])
    });

    it("should contain suite statistics", function () {
        var suitestats = window.testdata.statistics().suite[0];
        verifyBasicStatAttributes(suitestats, 'Suite', 4, 0, 'Suite');
    });

    it("should contain names and parent names for suite stats", function () {
        var statNoParents = window.testdata.statistics().suite[0];
        verifySuiteStatNames(statNoParents, 'Suite', '');
        var statWithParents = window.testdata.statistics().suite[1];
        verifySuiteStatNames(statWithParents, 'Sub', 'Suite . ');
    });

});

describe("Statistics percents and widths", function () {

    beforeEach(function (){
        window.data = [undefined,undefined,undefined,
                       [[["Critical Tests", 0,0,"","", ""],
                         ["All Tests", 2,1,"","", ""]],
                        [["<0.1% failed", 2000, 1, "", "", ""],
                         ["<0.1% passed", 1, 4000, "", "", ""],
                         ["0% failed", 100, 0, "", "", ""],
                         ["0% passed", 0, 30, "", "", ""],
                         ["0% passed", 5005, 4995, "", "", ""]],
                        []],
                       undefined];
    });

    function percentagesShouldBe(stat, passPercent, failPercent) {
        expect(stat.passPercent).toEqual(passPercent);
        expect(stat.failPercent).toEqual(failPercent);
    }

    function widthsShouldBe(stat, passWidth, failWidth) {
        expect(stat.passWidth).toEqual(passWidth);
        expect(stat.failWidth).toEqual(failWidth);
    }

    it("should count percentages and widths for zero tests to be zero", function (){
        var stat = window.testdata.statistics().total[0];
        percentagesShouldBe(stat, 0, 0);
        widthsShouldBe(stat, 0, 0);
    });

    it("should round floats to one digit in percentages and widths", function (){
        var stat = window.testdata.statistics().total[1];
        percentagesShouldBe(stat, 66.7, 33.3);
        widthsShouldBe(stat, 66.7, 33.3);
    });

    it("should guarantee that non-zero percentages are at least 0.1", function (){
        var stat = window.testdata.statistics().tag[0];
        percentagesShouldBe(stat, 99.9, 0.1);
        stat = window.testdata.statistics().tag[1];
        percentagesShouldBe(stat, 0.1, 99.9);
    });

    it("should guarantee that non-zero widths are at least 1", function (){
        var stat = window.testdata.statistics().tag[0];
        widthsShouldBe(stat, 99, 1);
        stat = window.testdata.statistics().tag[1];
        widthsShouldBe(stat, 1, 99);
    });

    it("should handle pass/fail percentages and widths of 0 and 100", function (){
        var stat = window.testdata.statistics().tag[2];
        percentagesShouldBe(stat, 100, 0);
        widthsShouldBe(stat, 100, 0);
        stat = window.testdata.statistics().tag[3];
        percentagesShouldBe(stat, 0, 100);
        widthsShouldBe(stat, 0, 100);
    });

    it("should guarantee that widths do not add up to over 100", function (){
        var stat = window.testdata.statistics().tag[4];
        percentagesShouldBe(stat, 50.1, 50);
        widthsShouldBe(stat, 50, 50);
    });
});
