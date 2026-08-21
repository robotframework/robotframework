import check from "bundle-text:./check.svg";
import close from "bundle-text:./close.svg";
import copy from "bundle-text:./copy.svg";
import globe from "bundle-text:./globe.svg";
import kwargs from "bundle-text:./kwargs.svg";
import namedOnly from "bundle-text:./named-only.svg";
import posOnly from "bundle-text:./pos-only.svg";
import robot from "bundle-text:./robot.svg";
import varargs from "bundle-text:./varargs.svg";

/**
 * The markers in front of an argument name and the icons of the copy button on
 * code blocks. The drawings next to this file are inlined by the build. They
 * become `<symbol>` elements that are referenced with `<use>`: repeating the
 * paths for every argument of a large library would add megabytes to the page.
 *
 * Stroked drawings must carry `fill`, `stroke` and the `stroke-*` attributes on
 * their paths. Only the content of the `<svg>` element ends up in the symbol,
 * so attributes set on the element itself would be lost.
 */
const ICONS: Record<string, string> = {
  "arg-icon-positional": posOnly,
  "arg-icon-named": namedOnly,
  "arg-icon-varargs": varargs,
  "arg-icon-kwargs": kwargs,
  "code-icon-copy": copy,
  "code-icon-check": check,
  "icon-robot": robot,
  "icon-globe": globe,
  "icon-close": close,
};

function symbol(id: string, svg: string): string {
  const viewBox = /viewBox="([^"]+)"/.exec(svg)?.[1] ?? "0 0 100 100";
  return (
    `<symbol id="${id}" viewBox="${viewBox}" fill="currentColor">` +
    svg
      .slice(
        svg.indexOf(">", svg.indexOf("<svg")) + 1,
        svg.lastIndexOf("</svg>"),
      )
      // Left behind by drawing programs; the identifiers would be duplicated
      // by every argument using the icon.
      .replace(
        /<defs[^>]*\/>|<defs[\s\S]*?<\/defs>|<metadata[\s\S]*?<\/metadata>/g,
        "",
      )
      .replace(/\s+id="[^"]*"/g, "")
      // Fixed colors are handed over to CSS. Matching the value itself would
      // be fragile: the build shortens `#ffffff` to `#fff`. `none` is left
      // alone, it is what makes the stroked icons hollow.
      .replace(/(fill|stroke)="#[0-9a-f]{3,8}"/gi, '$1="currentColor"')
      .replace(/(fill|stroke):\s*#[0-9a-f]{3,8}/gi, "$1:currentColor") +
    "</symbol>"
  );
}

/** Adds the definitions to the page; they render nothing by themselves. */
export function renderIcons(): void {
  if (document.querySelector(".icon-sprite")) {
    return;
  }
  const symbols = Object.entries(ICONS)
    .map(([id, svg]) => symbol(id, svg))
    .join("");
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<svg class="icon-sprite" aria-hidden="true">${symbols}</svg>`,
  );
}
