import { regexpEscape } from "./util";

test("regexp escape", () => {
  expect(regexpEscape("s[s")).toBe("s\\[s");
});
