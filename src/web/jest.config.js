/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  testEnvironment: "node",
  moduleNameMapper: {
    "^bundle-text:(.*)$": "$1",
  },
  transform: {
    "^.+\\.tsx?$": "ts-jest",
    "^.+\\.svg$": "<rootDir>/svg-transformer.js",
  },
};
