describe("Testing Matcher", function () {

    it("should match equal string", function () {
        expect(util.Matcher('xxx').matches('xxx')).toBeTruthy();
        expect(util.Matcher('xxx').matches('yyy')).not.toBeTruthy();
    });

    it("should match case and space sensitively", function () {
        var matches = util.Matcher('Hello World').matches;
        expect(matches('hello WORLD')).toBeTruthy();
        expect(matches('HELLOWORLD')).toBeTruthy();
        expect(matches('h e l l o   w o r l d')).toBeTruthy();
    });

    it("should support * wildcard", function () {
        var matches = util.Matcher('Hello*').matches;
        expect(matches('Hello')).toBeTruthy();
        expect(matches('Hello world')).toBeTruthy();
        expect(matches('HELLOWORLD')).toBeTruthy();
        expect(matches('Hillo')).not.toBeTruthy();
    });

    it("should support ? wildcard", function () {
        var matches = util.Matcher('H???o').matches;
        expect(matches('Hello')).toBeTruthy();
        expect(matches('happo')).toBeTruthy();
        expect(matches('Hello!')).not.toBeTruthy();
    });

    it("should escape regexp meta characters", function () {
        var matches = util.Matcher('a+.?').matches;
        expect(matches('a+.x')).toBeTruthy();
        expect(matches('A+.X')).toBeTruthy();
        expect(matches('a+.')).not.toBeTruthy();
        expect(matches('aaa')).not.toBeTruthy();
    });

    it("should support matching any", function () {
        var matchesAny = util.Matcher('ab?d*').matchesAny;
        expect(matchesAny(['xxx', 'abcd'])).toBeTruthy();
        expect(matchesAny(['xxx', 'abc'])).not.toBeTruthy();
        expect(matchesAny([])).not.toBeTruthy();
    });

});
