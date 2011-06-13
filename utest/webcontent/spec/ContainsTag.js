describe("Searching by tags", function () {

    it("should find tags by name", function () {
        expect(model.containsTag(['name'], 'name')).toBeTruthy();
        expect(model.containsTag(['x', 'y', 'z'], 'y')).toBeTruthy();
        expect(model.containsTag([], 'name')).not.toBeTruthy();
        expect(model.containsTag(['x', 'y'], 'notthere')).not.toBeTruthy();
    });

    it("should find tags case and space insensitively", function() {
        expect(model.containsTag(['name'], 'Name')).toBeTruthy();
        expect(model.containsTag(['NaMe'], 'name')).toBeTruthy();
        expect(model.containsTag(['xx', 'yy', 'zz'], 'y y')).toBeTruthy();
        expect(model.containsTag(['x      x', 'y y', 'z z'], 'XX')).toBeTruthy();
    });

    it("should find tags combined with &", function() {
        expect(model.containsTag(['x', 'y'], 'x & y', true)).toBeTruthy();
        expect(model.containsTag(['xx', 'Yy', 'ZZ'], 'Y Y & X X & zz', true)).toBeTruthy();
        expect(model.containsTag(['x', 'y'], 'xx & y', true)).not.toBeTruthy();
    });

    it("should find tags combined with NOT", function() {
        expect(model.containsTag(['x', 'y'], 'x NOT z', true)).toBeTruthy();
        expect(model.containsTag(['xx', 'yy'], 'X X NOT y NOT zz', true)).toBeTruthy();
        expect(model.containsTag(['X X', 'Y Y'], 'xx NOT yy', true)).not.toBeTruthy();
    });

    it("should find tags combined with patterns (* and ?)", function() {
        expect(model.containsTag(['x', 'y'], 'x*', true)).toBeTruthy();
        expect(model.containsTag(['xxxyyy'], 'x*', true)).toBeTruthy();
        expect(model.containsTag(['xyz'], 'x?z', true)).toBeTruthy();
        expect(model.containsTag(['-x-'], '*x*', true)).toBeTruthy();
        expect(model.containsTag(['x', 'y'], 'x', true)).toBeTruthy();
    });

    it("should find tags combined with patterns and & and NOT", function() {
        expect(model.containsTag(['xx', 'yy'], 'x* & y?', true)).toBeTruthy();
        expect(model.containsTag(['xxxyyy'], 'x* NOT y', true)).toBeTruthy();
        expect(model.containsTag(['xxxyyy'], 'x* NOT *y', true)).not.toBeTruthy();
    });

    it("should esacpe regex metacharacters in patterns", function() {
        expect(model.containsTag(['xyz'], 'x.*', true)).not.toBeTruthy();
        expect(model.containsTag(['x.z'], 'x.*', true)).toBeTruthy();
    });
});
