import en from "./en.json";
import fi from "./fi.json";

class Translate {
  private static instance: Translate;
  private languages: Array<any>;
  private language;

  private constructor() {
    this.languages = [en, fi];
    this.language = en;
  }

  public static getInstance(): Translate {
    if (!Translate.instance) {
      Translate.instance = new Translate();
    }

    return Translate.instance;
  }

  public getTranslation(key: string): string {
    if (key in this.language) {
      return this.language[key];
    }
    console.log("Wanring, missing translation for ");
    return "";
  }

  public setLanguage(lang: string) {
    if (lang == this.language.lang) {
      return false;
    }
    let found = false;
    this.languages.forEach((l) => {
      if (l.lang === lang) {
        this.language = l;
        found = true;
      }
    });
    return found;
  }

  public getLanguages() {
    return this.languages.map((l) => l.lang);
  }
}

export default Translate;
