function htmlEscape(htmlStr) {
  return htmlStr
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

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

export { htmlEscape, regexpEscape, delay };
