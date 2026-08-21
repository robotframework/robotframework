/**
 * Jest counterpart of Parcel's `bundle-text:` scheme: the SVG file is handed to
 * the importing module as a string, the same way the build does it.
 */
module.exports = {
  process(sourceText) {
    return { code: `module.exports = ${JSON.stringify(sourceText)};` };
  },
};
