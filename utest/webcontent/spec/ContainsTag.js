describe("Searching by tags", function () {

    it("should find tags by name", function () {
        expect(model.containsTag(['name'], 'name')).toBeTruthy();
        expect(model.containsTag(['x', 'y', 'z'], 'y')).toBeTruthy();
        expect(model.containsTag([], 'name')).not.toBeTruthy();
        expect(model.containsTag(['x', 'y'], 'notthere')).not.toBeTruthy();
    });

    it("should find tags case insensitively", function() {
        expect(model.containsTag(['name'], 'Name')).toBeTruthy();
        expect(model.containsTag(['NaMe'], 'namE')).toBeTruthy();
    });

    it("should find tags space insensitively", function() {
        expect(model.containsTag(['xx', 'yy', 'zz'], 'y y')).toBeTruthy();
        expect(model.containsTag(['x      x', 'y y', 'z z'], 'XX')).toBeTruthy();
    });

    it("should find tags underscore insensitively", function() {
        expect(model.containsTagPattern(['a_a_1', 'x'], 'a_a_*')).toBeTruthy();
        expect(model.containsTagPattern(['a_a_1', 'x'], 'a a *')).toBeTruthy();
        expect(model.containsTagPattern(['a a 1', 'x'], '_a__a__*_')).toBeTruthy();
    });

    it("should find tags with patterns * and ?", function() {
        expect(model.containsTagPattern(['x', 'y'], 'x*')).toBeTruthy();
        expect(model.containsTagPattern(['xxxyyy'], 'x*')).toBeTruthy();
        expect(model.containsTagPattern(['xyz'], 'x?z')).toBeTruthy();
        expect(model.containsTagPattern(['-x-'], '*x*')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x')).toBeTruthy();
    });

    it("should find tags combined with AND", function() {
        expect(model.containsTagPattern(['x', 'y'], 'xANDy')).toBeTruthy();
        expect(model.containsTagPattern(['xx', 'Yy', 'ZZ'], 'Y Y AND X X AND zz')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'xxANDy')).not.toBeTruthy();
    });

    it("should find tags combined with OR", function() {
        expect(model.containsTagPattern(['x', 'y'], 'xORy')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'xORz')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'z OR zz OR X')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'xxORyy')).not.toBeTruthy();
    });

    it("should find tags combined with OR and AND", function() {
        expect(model.containsTagPattern(['x', 'y'], 'x OR  y AND z')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'z OR  y AND x')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x AND y OR  z')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'z AND y OR  x')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x AND z OR  x AND y')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x OR  z AND x OR  y')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x AND z OR  y AND z')).not.toBeTruthy();
    });

    it("should find tags combined with NOT", function() {
        expect(model.containsTagPattern(['x', 'y'], 'xNOTz')).toBeTruthy();
        expect(model.containsTagPattern(['X X', 'Y Y'], 'xx NOT yy')).not.toBeTruthy();
        expect(model.containsTagPattern(['xx'], 'NOTyy')).toBeTruthy();
        expect(model.containsTagPattern([], 'NOTyy')).toBeTruthy();
        expect(model.containsTagPattern([], ' NOT yy')).toBeTruthy();
        expect(model.containsTagPattern(['yy'], ' NOT yy')).not.toBeTruthy();
    });

    it("should find tags combined with multiple NOTs", function() {
        expect(model.containsTagPattern(['a'], 'a NOT c NOT d')).toBeTruthy();
        expect(model.containsTagPattern(['a', 'b'], 'a NOT c NOT d')).toBeTruthy();
        expect(model.containsTagPattern(['a', 'b'], 'a NOT b NOT c')).not.toBeTruthy();
        expect(model.containsTagPattern(['a', 'b', 'c'], 'a NOT b NOT c')).not.toBeTruthy();
        expect(model.containsTagPattern(['x'], 'a NOT c NOT d')).not.toBeTruthy();
    });

    it("should find tags combined with NOT and AND", function() {
        expect(model.containsTagPattern(['x', 'y', 'z'], 'x NOT y AND z')).not.toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x NOT y AND z')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x NOT z AND y')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x AND y NOT z')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y', 'z'], 'x AND y NOT z')).not.toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x AND y NOT x AND z')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y', 'z'], 'x AND y NOT x AND z NOT y AND z')).not.toBeTruthy();
        expect(model.containsTagPattern(['x', 'y', 'z'], 'x AND y NOT x AND z NOT xxx')).not.toBeTruthy();
    });

    it("should find tags combined with NOT and OR", function() {
        expect(model.containsTagPattern(['a'], 'a NOT c OR d')).toBeTruthy();
        expect(model.containsTagPattern(['a', 'b'], 'a NOT c OR d')).toBeTruthy();
        expect(model.containsTagPattern(['a', 'b'], 'a NOT b OR c')).not.toBeTruthy();
        expect(model.containsTagPattern(['a', 'b', 'c'], 'a NOT b OR c')).not.toBeTruthy();
        expect(model.containsTagPattern(['x'], 'a NOT c OR d')).not.toBeTruthy();
        expect(model.containsTagPattern(['x'], 'a OR x NOT b')).toBeTruthy();
        expect(model.containsTagPattern(['x', 'y'], 'x OR a NOT y')).not.toBeTruthy();
    });

    it("should find tags combined with patterns and AND and NOT", function() {
        expect(model.containsTagPattern(['xx', 'yy'], 'x* AND y?')).toBeTruthy();
        expect(model.containsTagPattern(['xxxyyy'], 'x* NOT y*')).toBeTruthy();
        expect(model.containsTagPattern(['xxxyyy'], 'x* NOT *y')).not.toBeTruthy();
        expect(model.containsTagPattern(['xx', 'yy'], '* NOT x? NOT ?y')).not.toBeTruthy();
    });

    it("should escape regex meta characters in patterns", function() {
        expect(model.containsTagPattern(['xyz'], 'x.*')).not.toBeTruthy();
        expect(model.containsTagPattern(['+.z'], '+.?')).toBeTruthy();
    });
});
