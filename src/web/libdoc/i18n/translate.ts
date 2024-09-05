import en from "./en.json";

class Translate {
  private static instance: Translate;

  private constructor() {}

  public static getInstance(): Translate {
    if (!Translate.instance) {
      Translate.instance = new Translate();
    }

    return Translate.instance;
  }

  public getTranslation(key: string): string {
    if (key in en) {
      return en[key];
    }
    return "";
  }
}

export default Translate;
