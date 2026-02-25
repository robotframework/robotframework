import Mark from "mark.js";
import Handlebars from "handlebars";
import Storage from "./storage";
import Translations from "./i18n/translations";
import { createModal, showModal } from "./modal";
import { RuntimeLibdoc, ArgType } from "./types";
import { htmlEscape, regexpEscape, delay } from "./util";

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
    this.initTemplating(translations, libdoc);
  }

  private initTemplating(translate: Translations, libdoc: RuntimeLibdoc) {
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
    Handlebars.registerHelper(
      "renderTypeInfo",
      function (argType: ArgType, isReturnType: boolean) {
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
            const name = htmlEscape(argType.name);
            const renderTypeDocLink =
              argType.typedoc &&
              !(
                isReturnType &&
                libdoc.typedocs.find((td) => td.name === argType.typedoc)
                  ?.type === "Standard"
              );
            if (renderTypeDocLink) {
              html += `<a style="cursor: pointer;" class="type" data-typedoc=${argType.typedoc} title=${translate.translate("typeInfoDialog")}>${name}</a>`;
            } else {
              html += `<span class="type">${name}</span>`;
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
      },
    );
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
    let selectedShowTags = this.libdoc.showTags || [];
    let selectedHideTags = this.libdoc.hideTags || [];
    
    if (params.has("showtag")) {
      selectedShowTags = params.getAll("showtag");
    }
    if (params.has("hidetag")) {
      selectedHideTags = params.getAll("hidetag");
    }

    if (this.libdoc.tags.length) {
      this.libdoc.selectedShowTags = selectedShowTags;
      this.libdoc.selectedHideTags = selectedHideTags;
      
      this.renderTemplate("tags-shortcuts", { 
          tags: this.libdoc.tags, 
          selectedTags: selectedShowTags 
      }, "#show-tags-shortcuts-container");
      
      this.renderTemplate("tags-shortcuts", { 
          tags: this.libdoc.tags, 
          selectedTags: selectedHideTags 
      }, "#hide-tags-shortcuts-container");
      
      const updateTags = () => {
        const showSelect = document.getElementById("show-tags-shortcuts-container") as HTMLSelectElement;
        const hideSelect = document.getElementById("hide-tags-shortcuts-container") as HTMLSelectElement;
        
        const showVals = Array.from(showSelect.selectedOptions).map(opt => opt.value);
        const hideVals = Array.from(hideSelect.selectedOptions).map(opt => opt.value);
        
        this.tagsSearch(showVals, hideVals, window.location.hash);
      };

      document.getElementById("show-tags-shortcuts-container")!.onchange = updateTags;
      document.getElementById("hide-tags-shortcuts-container")!.onchange = updateTags;
      
      if (selectedShowTags.length > 0 || selectedHideTags.length > 0) {
          this.tagsSearch(selectedShowTags, selectedHideTags, window.location.hash);
      }
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
        const tag = (e.target! as HTMLSpanElement).innerText;
        const showSelect = document.getElementById("show-tags-shortcuts-container") as HTMLSelectElement;
        if (showSelect) {
            Array.from(showSelect.options).forEach(opt => {
                opt.selected = opt.value === tag;
            });
        }
        const hideSelect = document.getElementById("hide-tags-shortcuts-container") as HTMLSelectElement;
        if (hideSelect) {
            hideSelect.selectedIndex = -1;
        }
        this.tagsSearch([tag], [], window.location.hash);
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

  private tagsSearch(showTags: string[], hideTags: string[], hash?: string) {
    this.libdoc.selectedShowTags = showTags;
    this.libdoc.selectedHideTags = hideTags;
    
    const searchString = (document.getElementsByClassName("search-input")[0] as HTMLInputElement).value;
    
    const params = new URLSearchParams(window.location.search);
    params.delete("showtag");
    params.delete("hidetag");
    showTags.forEach(t => params.append("showtag", t));
    hideTags.forEach(t => params.append("hidetag", t));
    
    let search = params.toString();
    if (search) search = "?" + search;
    const url = window.location.pathname + search + (hash || "");
    
    this.applyFilters(searchString, showTags, hideTags);
    
    if (searchString) {
        this.highlightMatches(searchString, { name: true, args: true, doc: true, tags: true });
    }
    
    history.replaceState && history.replaceState(null, "", url);
    document.getElementById("keyword-shortcuts-container")!.scrollTop = 0;
  }

  private searching() {
    this.searchTime = Date.now();
    const searchString = (
      document.getElementsByClassName("search-input")![0] as HTMLInputElement
    ).value;
    
    const showTags = this.libdoc.selectedShowTags || [];
    const hideTags = this.libdoc.selectedHideTags || [];

    requestAnimationFrame(() => {
        this.applyFilters(searchString, showTags, hideTags, this.searchTime, () => {
            if (searchString) {
                this.highlightMatches(searchString, { name: true, args: true, doc: true, tags: true }, this.searchTime);
            }
            document.getElementById("keyword-shortcuts-container")!.scrollTop = 0;
        });
    });
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

  private applyFilters(
    searchString: string,
    showTags: string[],
    hideTags: string[],
    givenSearchTime?: number,
    callback?: FrameRequestCallback,
  ) {
    if (givenSearchTime && givenSearchTime !== this.searchTime) {
      return;
    }
    
    const hasSearch = searchString.length > 0;
    let searchRegexp: RegExp | null = null;
    if (hasSearch) {
        searchRegexp = new RegExp(regexpEscape(searchString), "i");
    }
    const test = searchRegexp ? searchRegexp.test.bind(searchRegexp) : () => false;

    let result = {} as RuntimeLibdoc;
    let keywordMatchCount = 0;
    result.keywords = this.libdoc.keywords.map((orig) => {
      const kw = { ...orig };
      kw.hidden = false;

      if (showTags.length > 0) {
          const matchesShow = showTags.some(t => {
              if (t === "[No tags]") return kw.tags.length === 0;
              return kw.tags.includes(t);
          });
          if (!matchesShow) kw.hidden = true;
      }

      if (hideTags.length > 0) {
          const matchesHide = hideTags.some(t => {
              if (t === "[No tags]") return kw.tags.length === 0;
              return kw.tags.includes(t);
          });
          if (matchesHide) kw.hidden = true;
      }

      if (hasSearch && !kw.hidden) {
          const matchesSearch = test(kw.name) || test(kw.args) || test(kw.doc) || kw.tags.some(test);
          if (!matchesSearch) kw.hidden = true;
      }

      if (!kw.hidden) keywordMatchCount++;
      return kw;
    });
    
    this.renderLibdocTemplate("keyword-shortcuts", result);
    this.renderKeywords(result);
    
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
    this.libdoc.selectedShowTags = [];
    this.libdoc.selectedHideTags = [];
    
    const showSelect = document.getElementById("show-tags-shortcuts-container") as HTMLSelectElement;
    if (showSelect) showSelect.selectedIndex = -1;
    
    const hideSelect = document.getElementById("hide-tags-shortcuts-container") as HTMLSelectElement;
    if (hideSelect) hideSelect.selectedIndex = -1;

    this.applyFilters("", [], []);
    
    history.replaceState && history.replaceState(null, "", location.pathname);
  }

  private clearSearch() {
    (
      document.getElementsByClassName("search-input")[0] as HTMLInputElement
    ).value = "";
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
