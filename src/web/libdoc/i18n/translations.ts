import translations from "./translations.json";

class Translations {
  private static instance: Translations;
  private language;

  private constructor(defaultLang: string) {
    this.setLanguage(defaultLang);
  }

  public static getInstance(defaultLang: string): Translations {
    if (!Translations.instance) {
      Translations.instance = new Translations(defaultLang || "en");
    }
    return Translations.instance;
  }

  public translate(key: string): string {
    if (key in this.language) {
      return this.language[key];
    }
    console.log("Warning, missing translation for", key);
    return "";
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
