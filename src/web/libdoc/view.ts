import Mark from "mark.js";
import Handlebars from "handlebars";
import Storage from "./storage";
import Translations from "./i18n/translations";
import { createModal, showModal } from "./modal";
import { renderIcons } from "./icons/icons";
import { RuntimeLibdoc, ArgType } from "./types";
import { htmlEscape, regexpEscape, delay } from "./util";

const ARG_KIND_ICONS: Record<string, string> = {
  POSITIONAL_ONLY: "positional",
  NAMED_ONLY: "named",
  VAR_POSITIONAL: "varargs",
  VAR_NAMED: "kwargs",
};

const ARG_KIND_KEYS: Record<string, string> = {
  POSITIONAL_OR_NAMED: "argKindPositionalOrNamed",
  POSITIONAL_ONLY: "argKindPositionalOnly",
  NAMED_ONLY: "argKindNamedOnly",
  VAR_POSITIONAL: "argKindVarArgs",
  VAR_NAMED: "argKindVarNamed",
};

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
  resizeListenerAdded = false;
  copyRevealAdded = false;
  resizeTimer?: ReturnType<typeof setTimeout>;
  scrollAnchor: { element: HTMLElement; top: number } | null = null;
  restoringAnchor = false;
  anchorUpdateQueued = false;
  resizing = false;
  lastWidth = 0;
  titleScrolled = false;

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
    Handlebars.registerHelper("isArgMarker", function (kind: string) {
      return kind === "NAMED_ONLY_MARKER" || kind === "POSITIONAL_ONLY_MARKER";
    });
    Handlebars.registerHelper("hasDefaults", function (args) {
      return (
        Array.isArray(args) && args.some((arg) => arg.defaultValue !== null)
      );
    });
    Handlebars.registerHelper("hasDocs", function (args) {
      return Array.isArray(args) && args.some((arg) => arg.doc);
    });
    // Raises maps an exception name to its documentation, which is mandatory
    // today but may not stay that way.
    Handlebars.registerHelper("anyValue", function (dict) {
      return !!dict && Object.values(dict).some((value) => value);
    });
    Handlebars.registerHelper("argKindIcon", function (kind: string) {
      return ARG_KIND_ICONS[kind] ?? "";
    });
    Handlebars.registerHelper(
      "argKindInfo",
      function (kind: string, required: boolean) {
        const how = translate.translate(
          ARG_KIND_KEYS[kind] ?? ARG_KIND_KEYS.POSITIONAL_OR_NAMED,
        );
        // Variable arguments take whatever is left over, so being required
        // says nothing about them.
        if (kind === "VAR_POSITIONAL" || kind === "VAR_NAMED") {
          return how;
        }
        const must = translate.translate(
          required ? "argRequired" : "argOptional",
        );
        return `${must} \u00b7 ${how}`;
      },
    );
    Handlebars.registerHelper("hasTypes", function (args) {
      return Array.isArray(args) && args.some((arg) => arg.type);
    });
    // The documentation cell spans the signature columns, and which of those
    // exist depends on the arguments.
    Handlebars.registerHelper(
      "signatureColumns",
      function (showDefault: boolean, showType: boolean) {
        return 1 + (showDefault ? 1 : 0) + (showType ? 1 : 0);
      },
    );
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
    this.registerPartial("argsSection", "arguments-section-template");
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
    renderIcons();
    this.renderTemplates();
    this.initTagSearch();
    this.initHashEvents();
    this.initLanguageMenu();
    setTimeout(() => {
      if (this.storage.get("keyword-wall") === "open") {
        this.openKeywordWall();
      }
    }, 0);
    if (!document.getElementById("modal-background")) {
      createModal(this.translations.translate("closeDialog"));
    }
    this.addCopyButtons();
    requestAnimationFrame(() => {
      this.updateDocClamping();
      this.updateTitleFit();
    });
    if (!this.resizeListenerAdded) {
      this.resizeListenerAdded = true;
      window.addEventListener(
        "scroll",
        () => {
          this.updateTitleSize();
          this.queueAnchorUpdate();
        },
        { passive: true },
      );
      this.updateTitleSize();
      this.initArgKindInfo();
      this.initResizeHandling();
      window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", ({ matches }) => {
          if (!this.libdoc.theme) {
            document.documentElement.setAttribute(
              "data-theme",
              matches ? "dark" : "light",
            );
          }
        });
    }
  }

  /**
   * Touch has no hover, so the explanation of an argument kind is opened by
   * tapping the symbol and closed by tapping anywhere else.
   */
  private initArgKindInfo() {
    document.addEventListener("pointerup", (event) => {
      const symbol = (event.target as HTMLElement)?.closest?.(
        ".arg-kind[aria-label]",
      );
      document
        .querySelectorAll(".arg-kind.show-info")
        .forEach((shown) => shown.classList.remove("show-info"));
      if (event.pointerType !== "mouse") {
        symbol?.classList.add("show-info");
      }
    });
  }

  private initResizeHandling() {
    this.lastWidth = window.innerWidth;
    window.addEventListener("resize", () => {
      // Mobile browsers fire `resize` while scrolling, because hiding the
      // address bar changes the window height. Nothing here depends on the
      // height, and restoring the reading position for such an event undoes
      // the very scrolling that caused it.
      if (window.innerWidth === this.lastWidth) {
        return;
      }
      this.lastWidth = window.innerWidth;
      // Measuring forces a layout of the whole document, and dragging a window
      // edge fires this far more often than the screen is repainted.
      this.resizing = true;
      clearTimeout(this.resizeTimer);
      this.resizeTimer = setTimeout(() => {
        this.resizing = false;
        this.updateTitleFit();
        this.updateDocClamping();
        this.restoreScrollAnchor();
      }, 200);
    });
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
    this.updateDocClamping();
  }

  /** The title only has room to be big while the top of the page is visible. */
  private updateTitleSize() {
    const scrolled = window.scrollY > 40;
    if (scrolled !== this.titleScrolled) {
      this.titleScrolled = scrolled;
      document.documentElement.classList.toggle("scrolled", scrolled);
    }
  }

  /**
   * Short library names fit into the compact bar at their full size, so only
   * the ones that do not are made smaller. Measured off screen because the
   * title itself is clipped, and only when the layout changes.
   */
  private updateTitleFit() {
    const title = document.querySelector<HTMLElement>(".libdoc-title");
    const heading = title?.querySelector<HTMLElement>("h1");
    if (!title || !heading) {
      return;
    }
    const root = document.documentElement;
    const scrolled = root.classList.contains("scrolled");
    root.classList.remove("scrolled");
    const style = getComputedStyle(heading);
    const probe = document.createElement("span");
    probe.style.cssText =
      "position:absolute;visibility:hidden;white-space:nowrap;" +
      `font:${style.fontStyle} ${style.fontWeight} ${style.fontSize}/${style.lineHeight} ${style.fontFamily}`;
    probe.textContent = heading.textContent;
    document.body.appendChild(probe);
    const needed = probe.getBoundingClientRect().width;
    probe.remove();
    if (scrolled) {
      root.classList.add("scrolled");
    }
    root.classList.toggle("title-fits", needed <= this.compactTitleWidth());
  }

  /** Room the name has in the compact bar, without its horizontal padding. */
  private compactTitleWidth(): number {
    const padding = 16;
    if (window.innerWidth < 900) {
      // The bar spans the window; the language and hamburger buttons sit on it.
      return window.innerWidth - 108 - padding;
    }
    const overview = document.querySelector<HTMLElement>(".libdoc-overview");
    const width = overview?.getBoundingClientRect().width || 300;
    return Math.min(width, 300) - padding;
  }

  /**
   * Resizing changes the height of everything above the reading position --
   * the keyword list collapses, arguments switch between rows and columns --
   * which would otherwise scroll the keyword being read out of view. The
   * topmost visible section is remembered while scrolling and put back to the
   * same place once the layout has changed.
   */
  private queueAnchorUpdate() {
    if (this.restoringAnchor || this.anchorUpdateQueued || this.resizing) {
      return;
    }
    // Measuring on every scroll event would force a layout per frame. Once per
    // 150ms is enough: the position is only read when the window is resized.
    this.anchorUpdateQueued = true;
    setTimeout(() => {
      this.anchorUpdateQueued = false;
      // A resize started in the meantime would already have changed the layout.
      if (!this.resizing && !this.restoringAnchor) {
        this.updateScrollAnchor();
      }
    }, 150);
  }

  private updateScrollAnchor() {
    // The section starting closest above the reading line fills the top of the
    // window. The first one merely reaching into it would be the previous,
    // mostly scrolled away section, whose height changes on resize as well.
    const readingLine = 100;
    let anchor: { element: HTMLElement; top: number } | null = null;
    document
      .querySelectorAll<HTMLElement>(
        "#introduction-container, .kw-row, .keyword-container, .data-type-container",
      )
      .forEach((element) => {
        const { top, height } = element.getBoundingClientRect();
        if (height && top <= readingLine) {
          anchor = { element, top };
        }
      });
    this.scrollAnchor = anchor;
  }

  private restoreScrollAnchor() {
    const anchor = this.scrollAnchor;
    if (!anchor || !anchor.element.isConnected) {
      return;
    }
    const delta = anchor.element.getBoundingClientRect().top - anchor.top;
    if (!delta) {
      return;
    }
    this.restoringAnchor = true;
    const details = document.querySelector<HTMLElement>(".libdoc-details");
    if (details && details.scrollHeight > details.clientHeight + 1) {
      details.scrollTop += delta;
    } else {
      window.scrollBy(0, delta);
    }
    requestAnimationFrame(() => {
      this.restoringAnchor = false;
    });
  }

  /**
   * Documentation is clamped to four lines with CSS. Only documentation that
   * really is too long gets the `more...` button and becomes clickable.
   */
  private updateDocClamping() {
    const wraps: HTMLElement[] = [];
    const docs: HTMLElement[] = [];
    // Writes, reads and writes again in three passes. Interleaving them forces
    // a layout per argument, a thousand of them on a large library.
    document.querySelectorAll<HTMLElement>(".arg-doc-wrap").forEach((wrap) => {
      const doc = wrap.querySelector<HTMLElement>(".arg-doc");
      if (!doc) {
        return;
      }
      wrap.querySelectorAll(".doc-more").forEach((more) => more.remove());
      doc.classList.add("clamped");
      doc.classList.remove("truncated");
      doc.onclick = null;
      wraps.push(wrap);
      docs.push(doc);
    });
    // Hidden documentation -- filtered out by the search, not laid out yet --
    // measures zero and would look like it fits. It stays clamped, which is
    // how the template renders it anyway.
    const measured = docs.map((doc) => ({
      known: doc.clientHeight > 0,
      overflowing: doc.scrollHeight > doc.clientHeight + 1,
    }));
    docs.forEach((doc, index) => {
      const wrap = wraps[index];
      if (!measured[index].known) {
        return;
      }
      if (!measured[index].overflowing) {
        doc.classList.remove("clamped");
        return;
      }
      doc.classList.add("truncated");
      // A button, not a span, so that the keyboard reaches it.
      const more = document.createElement("button");
      more.type = "button";
      more.classList.add("doc-more");
      more.textContent = this.translations.translate("more");
      more.title = this.translations.translate("argInfoDialog");
      wrap.appendChild(more);
      const showDetails = (event: Event) => {
        event.stopPropagation();
        this.showArgDocModal(wrap);
      };
      doc.onclick = showDetails;
      more.onclick = showDetails;
    });
  }

  private showArgDocModal(wrap: HTMLElement) {
    const group = wrap.closest("tbody");
    const doc = wrap.querySelector(".arg-doc");
    if (!group || !doc) {
      return;
    }
    const container = document.createElement("div");
    container.classList.add("arg-detail-container");

    const heading = document.createElement("h2");
    const name = group.querySelector(".arg-name, .raise-name");
    if (name) {
      heading.appendChild(name.cloneNode(true));
    } else {
      heading.textContent = this.translations.translate("returns");
    }
    container.appendChild(heading);

    const meta = document.createElement("div");
    meta.classList.add("arg-detail-meta");
    const defaultValue = group.querySelector(".arg-default-value");
    if (defaultValue) {
      meta.appendChild(this.argDetailItem("default", defaultValue.outerHTML));
    }
    const type = group.querySelector(".arg-cell-type");
    if (type?.textContent?.trim()) {
      meta.appendChild(this.argDetailItem("type", type.innerHTML));
    }
    if (meta.childElementCount) {
      container.appendChild(meta);
    }

    const fullDoc = doc.cloneNode(true) as HTMLElement;
    fullDoc.classList.remove("clamped", "truncated");
    container.appendChild(fullDoc);
    showModal(container);
  }

  private argDetailItem(labelKey: string, html: string) {
    const item = document.createElement("span");
    const label = document.createElement("span");
    label.classList.add("arg-detail-label");
    label.textContent = `${this.translations.translate(labelKey)}:`;
    item.appendChild(label);
    const value = document.createElement("span");
    value.innerHTML = html;
    // Type links open the data type modal and cannot be nested into this one.
    value.querySelectorAll("a.type").forEach((link) => {
      const plain = document.createElement("span");
      plain.classList.add("type");
      plain.textContent = link.textContent;
      link.replaceWith(plain);
    });
    item.appendChild(value);
    return item;
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
      elem.addEventListener("click", () => {
        this.tagSearch(elem.textContent?.trim() ?? "");
      });
    });
    this.registerTypeDocHandlers("#keywords-container");
    this.updateDocClamping();
    document.getElementById("keyword-statistics-header")!.innerText =
      "" + this.libdoc.keywords.length;
    this.addCopyButtons();
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

  /**
   * Every documentation format renders code blocks differently: Markdown wraps
   * them into `<div class="code">`, reST and HTML put the class on the `<pre>`
   * itself and Robot Framework format leaves a bare `<pre>`. Looking for the
   * `<pre>` covers them all. Blocks that are not already wrapped get a wrapper,
   * because the button has to be positioned by an element that does not scroll
   * with the code.
   */
  private addCopyButtons() {
    if (!navigator.clipboard) {
      return;
    }
    this.initCopyButtonReveal();
    document.querySelectorAll<HTMLElement>(".doc pre").forEach((pre) => {
      const block = this.codeBlockOf(pre);
      if (block.querySelector(".code-copy-btn")) {
        return;
      }
      // Read before the button is added so that it cannot end up in the copy.
      // `textContent` and not `innerText`: the latter depends on the layout and
      // is empty for everything the browser has not laid out yet.
      const code = (pre.textContent ?? "").replace(/\s+$/, "");
      if (!code) {
        return;
      }
      block.appendChild(this.createCopyButton(code));
    });
  }

  /**
   * The button only shows while its block is hovered, which touch devices
   * cannot do. There tapping the block reveals it, and tapping anywhere else
   * hides it again.
   */
  private initCopyButtonReveal() {
    if (this.copyRevealAdded) {
      return;
    }
    this.copyRevealAdded = true;
    document.addEventListener("pointerdown", (event) => {
      // A mouse has hover and needs no help. Deciding by the pointer instead of
      // by a media query also covers devices that have both.
      if (event.pointerType === "mouse") {
        return;
      }
      const block = (event.target as HTMLElement).closest(
        ".doc .code, .doc .code-block",
      );
      document.querySelectorAll(".copy-visible").forEach((visible) => {
        if (visible !== block) {
          visible.classList.remove("copy-visible");
        }
      });
      block?.classList.add("copy-visible");
    });
  }

  private codeBlockOf(pre: HTMLElement): HTMLElement {
    const parent = pre.parentElement;
    if (
      parent?.classList.contains("code") ||
      parent?.classList.contains("code-block")
    ) {
      return parent;
    }
    const block = document.createElement("div");
    block.classList.add("code-block");
    pre.replaceWith(block);
    block.appendChild(pre);
    return block;
  }

  private createCopyButton(code: string): HTMLButtonElement {
    const copyLabel = this.translations.translate("copyCode");
    const copiedLabel = this.translations.translate("codeCopied");
    const button = document.createElement("button");
    button.type = "button";
    button.classList.add("code-copy-btn");
    button.title = copyLabel;
    button.setAttribute("aria-label", copyLabel);
    // Both icons are rendered and only swapped by CSS, which lets the change
    // be animated and keeps the button from resizing.
    button.innerHTML =
      '<svg class="code-copy-icon" aria-hidden="true">' +
      '<use href="#code-icon-copy" /></svg>' +
      '<svg class="code-check-icon" aria-hidden="true">' +
      '<use href="#code-icon-check" /></svg>';
    let reset: NodeJS.Timeout;
    button.addEventListener("click", () => {
      navigator.clipboard
        .writeText(code)
        .then(() => {
          button.classList.add("copied");
          button.title = copiedLabel;
          button.setAttribute("aria-label", copiedLabel);
          clearTimeout(reset);
          reset = setTimeout(() => {
            button.classList.remove("copied");
            button.title = copyLabel;
            button.setAttribute("aria-label", copyLabel);
          }, 1500);
        })
        .catch(() => {
          // Copying can be denied by the browser. Nothing to show then.
        });
    });
    return button;
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
        "#keywords-container .match .tags .tag-link",
      );
      if (include.tagsExact) {
        // Filtering by a tag highlights that tag in every matching keyword the
        // same way search results are highlighted.
        const filtered: Array<Element> = [];
        matches.forEach((elem) => {
          if (elem.textContent?.trim().toUpperCase() == string.toUpperCase()) {
            filtered.push(elem);
          }
        });
        new Mark(filtered).mark(string);
      } else {
        new Mark(Array.from(matches)).mark(string);
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
