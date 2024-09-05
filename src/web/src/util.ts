function regexpEscape(string: string) {
  return string.replace(/[-[\]{}()+?*.,\\^$|#]/g, "\\$&");
}

const delay = (function () {
  let timer: NodeJS.Timeout;
  return function (callback: () => void, ms: number) {
    clearTimeout(timer);
    timer = setTimeout(callback, ms);
  };
})();

export { regexpEscape, delay };
