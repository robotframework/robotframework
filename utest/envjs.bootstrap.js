load('../ext-lib/jasmine-reporters/ext/env.rhino.1.2.js');

Envjs.scriptTypes['text/javascript'] = true;
var specFile = arguments[0];
console.log("Loading: " + specFile);
window.location = specFile
