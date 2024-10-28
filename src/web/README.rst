Robot Framework web projects
============================

This directory contains the Robot Framework HTML frontend for libdoc. Eventually, also log and report will be moved to the same tech stack.

Tech
----

This prototype uses following technologies:

- [Parcel](https://parceljs.org) is used to create development and (minified) shipping bundles. It offers a very low-configuration way of creating standalone HTML files, which contain all the code and styles inlined.
- [Typescript](https://www.typescriptlang.org) is used to write the business logic. It offers better development ergomonics than plain Javascript.
- [Handlebars](https://handlebarsjs.com) is used for templating. Using either HTML `<template>` tags + code, or generating HTML purely from code were also considered. However, a template system makes authoring complex HTML much simpler, since creating nested structures purely in code leads to hard-to-maintain solutions almost inevitably. Handlebars enables re-use of existing templates with minor modifications, while it offers some new feature that help e.g. with localisation.

Unit test are written using [Jest](https://jestjs.io).

Development
-----------

Install dependencies::

    npm install

Run::

    npm run start

The development server starts at `localhost:1234`.

Test::

    npm test


Code formatting conventions
--------------------------

Prettier is used to format code, and it can be run manually by::

    npm run pretty

