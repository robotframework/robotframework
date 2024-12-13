import Storage from "./storage";
import Translations from "./i18n/translations";
import { Libdoc } from "./types";
import View from "./view";

function render(libdoc: Libdoc) {
  const storage = new Storage("libdoc");
  const translations = Translations.getInstance(libdoc.lang);
  const view = new View(libdoc, storage, translations);
  view.render();
}

export default render;
