import translations from "./translations.json";

class Translations {
  private static instance: Translations;
  private language;

  private constructor(defaultLang: string) {
    this.setLanguage(defaultLang);
  }

  public static getInstance(defaultLang?: string | null): Translations {
    if (!Translations.instance) {
      Translations.instance = new Translations(defaultLang || "en");
    }
    return Translations.instance;
  }

  public translate(key: string): string {
    const translation = this.language[key];
    if (typeof translation === "string") {
      return translation;
    }
    return translations["en"][key];
  }

  /**
   * Fills in the placeholders of a translation, such as the `{alias}` and
   * `{type}` of `typeAliasFor`. A translation that lost a placeholder would
   * silently drop what it stands for -- the link to the type an alias resolves
   * to, in that case -- so the English text is used when one is missing.
   */
  public interpolate(key: string, values: Record<string, string>): string {
    const translation = this.translate(key);
    const complete = Object.keys(values).every((name) =>
      translation.includes(`{${name}}`),
    );
    // A replacement is given as a function, because `$&` and its like in the
    // replacing text would otherwise be read as a backreference.
    return Object.entries(values).reduce(
      (text, [name, value]) => text.replace(`{${name}}`, () => value),
      complete ? translation : translations["en"][key],
    );
  }

  public setLanguage(lang: string) {
    if (this.language && lang == this.language.code) {
      return false;
    }
    let found = false;
    Object.keys(translations).forEach((langCode) => {
      if (langCode.toLowerCase() === lang.toLowerCase()) {
        this.language = translations[langCode];
        found = true;
      }
    });
    return found;
  }

  public getLanguageCodes() {
    return Object.keys(translations);
  }

  public currentLanguage() {
    return this.language.code;
  }
}

export default Translations;
