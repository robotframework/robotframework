import Mark from "mark.js";
import Handlebars from "handlebars";
import Storage from "./storage";
import Translations from "./i18n/translations";
import { createModal, showModal } from "./modal";
import { RuntimeLibdoc, ArgType } from "./types";
import { htmlEscape, regexpEscape, delay } from "./util";

// Feather Icons copy (MIT licence, https://feathericons.com)
const CLIPBOARD_SVG = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
// Heroicons check (MIT licence, https://heroicons.com)
const CHECK_SVG = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/></svg>`;

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
    window.addEventListener("resize", () => delay(() => this.updateDocClamping(), 100));
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
    Handlebars.registerHelper("or", function (a, b) {
      return a || b;
    });
    Handlebars.registerHelper(
      "hasVisibleReturnType",
      function (returnType: ArgType | null | undefined) {
        return (
          returnType !== null &&
          returnType !== undefined &&
          returnType.name !== "None"
        );
      },
    );
    Handlebars.registerHelper("dictSize", function (context) {
      if (context === null || context === undefined) {
        return 0;
      }
      return Object.keys(context).length;
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
    Handlebars.registerHelper("isArgMarker", function (kind: string) {
      return kind === "POSITIONAL_ONLY_MARKER" || kind === "NAMED_ONLY_MARKER";
    });
    this.registerPartial("arg", "argument-template");
    this.registerPartial("keyword", "keyword-template");
    this.registerPartial("dataType", "data-type-template");
    this.registerPartial("argsSection", "arguments-section-template");
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
    this.initThemeToggle();
    setTimeout(() => {
      if (this.storage.get("keyword-wall") === "open") {
        this.openKeywordWall();
      }
    }, 0);
    createModal();
    this.updateDocClamping();
    this.addCopyButtons();
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
    document.querySelectorAll(".tag-link").forEach((elem) => {
      elem.addEventListener("click", (e) => {
        this.tagSearch((e.target! as HTMLSpanElement).innerText);
      });
    });
    this.registerTypeDocHandlers("#keywords-container");
    document.getElementById("keyword-statistics-header")!.innerText =
      "" + this.libdoc.keywords.length;
    this.updateDocClamping();
    this.addCopyButtons();
  }

  private setTheme() {
    document.documentElement.setAttribute("data-theme", this.getTheme());
  }

  private getTheme() {
    const params = new URLSearchParams(window.location.search);
    if (params.has("theme")) return params.get("theme")!;
    const stored = localStorage.getItem("libdoc-theme");
    if (stored) return stored;
    if (this.libdoc.theme != null) return this.libdoc.theme;
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  private initThemeToggle() {
    document
      .getElementById("theme-toggle")
      ?.addEventListener("click", () => this.toggleTheme());
  }

  private toggleTheme() {
    const next =
      document.documentElement.getAttribute("data-theme") === "dark"
        ? "light"
        : "dark";
    document.documentElement.setAttribute("theme-toggled", "");
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("libdoc-theme", next);
  }

  private updateDocClamping() {
    document.querySelectorAll<HTMLElement>(".arg-doc").forEach((el) => {
      // Remove any controls injected by a previous call
      let sib = el.nextElementSibling;
      while (
        sib?.classList.contains("doc-more") ||
        sib?.classList.contains("doc-less")
      ) {
        const next = sib.nextElementSibling;
        sib.remove();
        sib = next as Element | null;
      }
      el.classList.remove("truncated");
      el.classList.add("clamped");
      el.onclick = null;

      if (el.scrollHeight > el.clientHeight) {
        el.classList.add("truncated");

        const more = document.createElement("span");
        more.className = "doc-more";
        more.textContent = this.translations.translate("more");
        el.after(more);

        const setExpanded = (expanded: boolean) => {
          if (expanded) {
            el.classList.remove("clamped", "truncated");
            more.style.display = "none";
            el.onclick = null;
            const less = document.createElement("span");
            less.className = "doc-less";
            less.textContent = this.translations.translate("less");
            less.onclick = () => {
              less.remove();
              setExpanded(false);
            };
            more.after(less);
          } else {
            el.classList.add("clamped", "truncated");
            more.style.display = "";
            el.onclick = () => setExpanded(true);
            more.onclick = () => setExpanded(true);
          }
        };

        el.onclick = () => setExpanded(true);
        more.onclick = () => setExpanded(true);
      } else {
        el.classList.remove("clamped");
      }
    });
  }

  private addCopyButtons() {
    if (!navigator.clipboard) return;
    document.querySelectorAll<HTMLElement>(".doc .code").forEach((block) => {
      if (block.querySelector(".code-copy-btn")) return;
      const btn = document.createElement("button");
      btn.className = "code-copy-btn";
      btn.title = this.translations.translate("copyCode");
      btn.innerHTML = CLIPBOARD_SVG;
      btn.addEventListener("click", () => {
        const pre = block.querySelector("pre");
        if (!pre) return;
        navigator.clipboard.writeText(pre.innerText).then(() => {
          btn.innerHTML = CHECK_SVG;
          setTimeout(() => {
            btn.innerHTML = CLIPBOARD_SVG;
          }, 1500);
        }).catch(() => {
          btn.innerHTML = CLIPBOARD_SVG;
        });
      });
      block.appendChild(btn);
    });
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
        "#keywords-container .match .tags span.tag-link",
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
    this.addCopyButtons();
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
