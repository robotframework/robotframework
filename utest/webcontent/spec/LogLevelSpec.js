describe("LogLevelController", function() {
    function checkCombination(min_level, default_level, should_show, expected_default, show_trace) {
        var controller = LogLevelController(min_level, default_level);
        expect(controller.showLogLevelSelector()).toEqual(should_show);
        if(should_show){
          expect(controller.defaultLogLevel()).toEqual(expected_default);
          expect(controller.showTrace()).toEqual(show_trace);
        }
    }

    it("Should select correct log level", function () {
        checkCombination("TRACE", "TRACE", true, 0, true);
        checkCombination("DEBUG", "INFO", true, 2, false);
        checkCombination("TRACE", "DEBUG", true, 1, true);
        checkCombination("INFO", "INFO", false);
        checkCombination("WARN", "INFO", false);
        checkCombination("DEBUG", "TRACE", true, 1, false);
    });
});
