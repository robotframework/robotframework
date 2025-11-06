import Mark from "mark.js";
import Handlebars from "handlebars";
import Storage from "./storage";
import Translations from "./i18n/translations";
import { createModal, showModal } from "./modal";
import { RuntimeLibdoc, ArgType } from "./types";
import { regexpEscape, delay } from "./util";

interface MatchInclude {
  args?: boolean;
  doc?: boolean;
  name?: boolean;
  tags?: boolean;
  tagsExact?: boolean;
}

class View {
  storage: Storage;
  libdoc: RuntimeLibdoc;
  translations: Translations;
  searchTime: number;

  constructor(
    libdoc: RuntimeLibdoc,
    storage: Storage,
    translations: Translations,
  ) {
    this.libdoc = libdoc;
    this.storage = storage;
    this.translations = translations;
    this.initTemplating(translations);
  }

  private initTemplating(translate: Translations) {
    Handlebars.registerHelper("t", function (key: string) {
      return translate.translate(key);
    });
    Handlebars.registerHelper("encodeURIComponent", function (value: string) {
      return encodeURIComponent(value);
    });
    Handlebars.registerHelper(
      "ifEquals",
      function (arg1: string, arg2: string, options) {
        return arg1 == arg2 ? options.fn(this) : options.inverse(this);
      },
    );
    Handlebars.registerHelper("ifNotNull", function (arg1, options) {
      return arg1 !== null ? options.fn(this) : options.inverse(this);
    });
    Handlebars.registerHelper("ifContains", function (elems, value, options) {
      return elems.indexOf(value) != -1
        ? options.fn(this)
        : options.inverse(this);
    });
    Handlebars.registerHelper("renderTypeInfo", function (argType: ArgType) {
      const renderTypeDocs = (argType: ArgType) => {
        if (argType.union) {
          let html = "";
          argType.nested.forEach((nested, index) => {
            if (index > 0) {
              html += " ";
            }
            html += renderTypeDocs(nested);
            if (index < argType.nested.length - 1) {
              html += " |";
            }
          });
          return html;
        } else {
          let html = "";
          if (argType.typedoc) {
            html += `<a style="cursor: pointer;" class="type" data-typedoc=${argType.typedoc} title=${translate.translate("typeInfoDialog")}>${argType.name}</a>`;
          } else {
            html += `<span class="type">${argType.name}</span>`;
          }
          if (argType.nested.length) {
            html += "[";
            argType.nested.forEach((nested, idx) => {
              html += renderTypeDocs(nested);
              if (idx < argType.nested.length - 1) {
                html += ",&nbsp;";
              }
            });
            html += "]";
          }
          return html;
        }
      };
      return renderTypeDocs(argType);
    });
    this.registerPartial("arg", "argument-template");
    this.registerPartial("keyword", "keyword-template");
    this.registerPartial("dataType", "data-type-template");
  }

  private registerPartial(name: string, id: string) {
    const content = document.getElementById(id)?.innerHTML;
    Handlebars.registerPartial(name, Handlebars.compile(content));
  }

  render() {
    document.title = this.libdoc.name;
    this.setTheme();
    this.renderTemplates();
    this.initTagSearch();
    this.initHashEvents();
    this.initLanguageMenu();
    setTimeout(() => {
      if (this.storage.get("keyword-wall") === "open") {
        this.openKeywordWall();
      }
    }, 0);
    createModal();
  }

  private renderTemplates() {
    this.renderLibdocTemplate("base", this.libdoc, "#root");
    if (this.libdoc.inits.length > 0) {
      this.renderImporting();
    }
    this.renderShortcuts();
    this.renderKeywords();
    this.renderLibdocTemplate("data-types");
    this.renderLibdocTemplate("footer");
  }

  private initHashEvents() {
    window.addEventListener(
      "hashchange",
      function () {
        (
          document.getElementsByClassName(
            "hamburger-menu",
          )[0]! as HTMLInputElement
        ).checked = false;
      },
      false,
    );
    window.addEventListener(
      "hashchange",
      function () {
        if (window.location.hash.indexOf("#type-") == 0) {
          const hash =
            "#type-modal-" + decodeURI(window.location.hash.slice(6));
          const typeDoc = document
            .querySelector(".data-types")!
            .querySelector(hash);
          if (typeDoc) {
            showModal(typeDoc);
          }
        }
      },
      false,
    );
    this.scrollToHash();
  }

  private initTagSearch() {
    const params = new URLSearchParams(window.location.search);
    let selectedTag = "";
    if (params.has("tag")) {
      selectedTag = params.get("tag")!;
      this.tagSearch(selectedTag, window.location.hash);
    }
    if (this.libdoc.tags.length) {
      this.libdoc.selectedTag = selectedTag;
      this.renderLibdocTemplate("tags-shortcuts");
      document.getElementById("tags-shortcuts-container")!.onchange = (e) => {
        const value = (e.target as HTMLSelectElement).selectedOptions[0].value;
        if (value != "") {
          this.tagSearch(value);
        } else {
          this.clearTagSearch();
        }
      };
    }
  }

  private initLanguageMenu() {
    this.renderTemplate("language", {
      languages: this.translations.getLanguageCodes(),
    });
    document.querySelectorAll("#language-container ul a")!.forEach((link) => {
      if (link.innerHTML === this.translations.currentLanguage()) {
        link.classList.toggle("selected");
      }
      link.addEventListener("click", () => {
        const changed = this.translations.setLanguage(link.innerHTML);
        if (changed) {
          this.render();
        }
      });
    });
    document
      .querySelector("#language-container button")!
      .addEventListener("click", () => {
        document
          .querySelector("#language-container ul")!
          .classList.toggle("hidden");
      });
  }

  private renderImporting() {
    this.renderLibdocTemplate("importing");
    this.registerTypeDocHandlers("#importing-container");
  }

  private renderShortcuts() {
    this.renderLibdocTemplate("shortcuts");
    document
      .getElementById("toggle-keyword-shortcuts")!
      .addEventListener("click", () => this.toggleShortcuts());
    document
      .querySelector(".clear-search")!
      .addEventListener("click", () => this.clearSearch());
    document
      .querySelector(".search-input")!
      .addEventListener("keydown", () => delay(() => this.searching(), 150));
    this.renderLibdocTemplate("keyword-shortcuts");
    document
      .querySelectorAll("a.match")
      .forEach((e) => e.addEventListener("click", this.closeMenu));
  }

  private registerTypeDocHandlers(container: string) {
    document.querySelectorAll(`${container} a.type`).forEach((elem) =>
      elem.addEventListener("click", (e) => {
        const typeDoc = (e.target as HTMLElement).dataset.typedoc;
        showModal(document.querySelector(`#type-modal-${typeDoc}`));
      }),
    );
  }

  private renderKeywords(libdoc: RuntimeLibdoc | null = null) {
    if (libdoc == null) {
      libdoc = this.libdoc;
    }
    this.renderLibdocTemplate("keywords", libdoc);
    document.querySelectorAll(".kw-tags span").forEach((elem) => {
      elem.addEventListener("click", (e) => {
        this.tagSearch((e.target! as HTMLSpanElement).innerText);
      });
    });
    this.registerTypeDocHandlers("#keywords-container");
    document.getElementById("keyword-statistics-header")!.innerText =
      "" + this.libdoc.keywords.length;
  }

  private setTheme() {
    document.documentElement.setAttribute("data-theme", this.getTheme());
  }

  private getTheme() {
    if (this.libdoc.theme != null) {
      return this.libdoc.theme;
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    } else {
      return "light";
    }
  }

  private scrollToHash() {
    if (window.location.hash) {
      const hash = window.location.hash.substring(1);
      const elem = document.getElementById(decodeURIComponent(hash));
      if (elem != null) {
        elem.scrollIntoView();
      }
    }
  }

  private tagSearch(tag: string, hash?: string) {
    (
      document.getElementsByClassName("search-input")[0] as HTMLInputElement
    ).value = "";
    const include = { tags: true, tagsExact: true };
    const url = window.location.pathname + "?tag=" + tag + (hash || "");
    this.markMatches(tag, include);
    this.highlightMatches(tag, include);
    history.replaceState && history.replaceState(null, "", url);
    document.getElementById("keyword-shortcuts-container")!.scrollTop = 0;
  }

  private clearTagSearch() {
    (
      document.getElementsByClassName("search-input")[0] as HTMLInputElement
    ).value = "";
    history.replaceState &&
      history.replaceState(null, "", window.location.pathname);
    this.resetKeywords();
  }

  private searching() {
    this.searchTime = Date.now();
    const value = (
      document.getElementsByClassName("search-input")![0] as HTMLInputElement
    ).value;
    const include = { name: true, args: true, doc: true, tags: true };

    if (value) {
      requestAnimationFrame(() => {
        this.markMatches(value, include, this.searchTime, () => {
          this.highlightMatches(value, include, this.searchTime);
          document.getElementById("keyword-shortcuts-container")!.scrollTop = 0;
        });
      });
    } else {
      this.resetKeywords();
    }
  }

  private highlightMatches(
    string: string,
    include: MatchInclude,
    givenSearchTime?: number,
  ) {
    if (givenSearchTime && givenSearchTime !== this.searchTime) {
      return;
    }
    const shortcuts = document.querySelectorAll("#shortcuts-container .match");
    const keywords = document.querySelectorAll("#keywords-container .match");
    if (include.name) {
      new Mark(shortcuts).mark(string);
      new Mark(keywords).mark(string);
    }
    if (include.args) {
      new Mark(
        document.querySelectorAll("#keywords-container .match .args"),
      ).mark(string);
    }
    if (include.doc) {
      new Mark(
        document.querySelectorAll("#keywords-container .match .doc"),
      ).mark(string);
    }
    if (include.tags) {
      const matches = document.querySelectorAll(
        "#keywords-container .match .tags a, #tags-shortcuts-container .match .tags a",
      );
      if (include.tagsExact) {
        const filtered: Array<Element> = [];
        matches.forEach((elem) => {
          if (elem.textContent?.toUpperCase() == string.toUpperCase())
            filtered.push(elem);
        });
        new Mark(filtered).mark(string);
      } else {
        new Mark(matches).mark(string);
      }
    }
  }

  private markMatches(
    pattern: string,
    include: MatchInclude,
    givenSearchTime?: number,
    callback?: FrameRequestCallback,
  ) {
    if (givenSearchTime && givenSearchTime !== this.searchTime) {
      return;
    }
    let patternRegexp = regexpEscape(pattern);
    if (include.tagsExact) {
      patternRegexp = "^" + patternRegexp + "$";
    }
    const regexp = new RegExp(patternRegexp, "i");
    const test = regexp.test.bind(regexp);
    let result = {} as RuntimeLibdoc;
    let keywordMatchCount = 0;
    result.keywords = this.libdoc.keywords.map((orig) => {
      const kw = { ...orig };
      kw.hidden =
        !(include.name && test(kw.name)) &&
        !(include.args && test(kw.args)) &&
        !(include.doc && test(kw.doc)) &&
        !(include.tags && kw.tags.some(test));
      if (!kw.hidden) keywordMatchCount++;
      return kw;
    });
    this.renderLibdocTemplate("keyword-shortcuts", result);
    this.renderKeywords(result);
    if (this.libdoc.tags.length) {
      this.libdoc.selectedTag = include.tagsExact ? pattern : "";
      this.renderLibdocTemplate("tags-shortcuts");
    }
    document.getElementById("keyword-statistics-header")!.innerText =
      keywordMatchCount + " / " + result.keywords.length;
    if (keywordMatchCount === 0)
      (
        document.querySelector("#keywords-container table") as HTMLTableElement
      ).innerHTML = "";
    if (callback) {
      requestAnimationFrame(callback);
    }
  }

  private closeMenu() {
    (
      document.getElementById("hamburger-menu-input")! as HTMLInputElement
    ).checked = false;
  }

  private openKeywordWall() {
    const shortcuts = document.getElementsByClassName("shortcuts")[0];
    shortcuts.classList.add("keyword-wall");
    this.storage.set("keyword-wall", "open");
    const button = document.getElementById("toggle-keyword-shortcuts");
    button!.innerText = "-";
  }

  private closeKeywordWall() {
    const shortcuts = document.getElementsByClassName("shortcuts")[0];
    shortcuts.classList.remove("keyword-wall");
    this.storage.set("keyword-wall", "close");
    const button = document.getElementById("toggle-keyword-shortcuts");
    button!.innerText = "+";
  }

  private toggleShortcuts() {
    const shortcuts = document.getElementsByClassName("shortcuts")[0];
    if (shortcuts.classList.contains("keyword-wall")) {
      this.closeKeywordWall();
    } else {
      this.openKeywordWall();
    }
  }

  private resetKeywords() {
    this.renderLibdocTemplate("keyword-shortcuts");
    this.renderKeywords();
    if (this.libdoc.tags.length) {
      this.libdoc.selectedTag = "";
      this.renderLibdocTemplate("tags-shortcuts");
    }
    history.replaceState && history.replaceState(null, "", location.pathname);
  }

  private clearSearch() {
    (
      document.getElementsByClassName("search-input")[0] as HTMLInputElement
    ).value = "";
    const tagsSelect = document.getElementById("tags-shortcuts-container");
    if (tagsSelect) {
      (tagsSelect as HTMLSelectElement).selectedIndex = 0;
    }
    this.resetKeywords();
  }

  private renderLibdocTemplate(
    name: string,
    libdoc: RuntimeLibdoc | null = null,
    container_selector: string = "",
  ) {
    if (libdoc == null) {
      libdoc = this.libdoc;
    }
    this.renderTemplate(name, libdoc, container_selector);
  }

  private renderTemplate(
    name: string,
    data: any,
    container_selector: string = "",
  ) {
    const template = document.getElementById(`${name}-template`)?.innerHTML;
    const compiled_template = Handlebars.compile(template);

    if (container_selector === "") {
      container_selector = `#${name}-container`;
    }

    const target = document.body.querySelector(container_selector)!;
    target.innerHTML = compiled_template(data);
  }
}

export default View;
