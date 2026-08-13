import kwargs from "bundle-text:./kwargs.svg";
import namedOnly from "bundle-text:./named-only.svg";
import posOnly from "bundle-text:./pos-only.svg";
import varargs from "bundle-text:./varargs.svg";

/**
 * The markers in front of an argument name. The drawings next to this file are
 * inlined by the build. They become `<symbol>` elements that the arguments
 * reference with `<use>`: repeating the paths for every argument of a large
 * library would add megabytes to the page.
 */
const ICONS: Record<string, string> = {
  "arg-icon-positional": posOnly,
  "arg-icon-named": namedOnly,
  "arg-icon-varargs": varargs,
  "arg-icon-kwargs": kwargs,
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
export function renderArgKindIcons(): void {
  if (document.querySelector(".arg-icon-sprite")) {
    return;
  }
  const symbols = Object.entries(ICONS)
    .map(([id, svg]) => symbol(id, svg))
    .join("");
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<svg class="arg-icon-sprite" aria-hidden="true">${symbols}</svg>`,
  );
}
