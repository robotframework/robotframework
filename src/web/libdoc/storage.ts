class Storage {
  prefix = "robot-framework-";
  storage: Object;

  constructor(user: string = "") {
    if (user) {
      this.prefix += user + "-";
    }
    this.storage = this.getStorage();
  }
  getStorage() {
    // Use localStorage if it's accessible, normal object otherwise.
    // Inspired by https://stackoverflow.com/questions/11214404
    try {
      localStorage.setItem(this.prefix, this.prefix);
      localStorage.removeItem(this.prefix);
      return localStorage;
    } catch (exception) {
      return {};
    }
  }

  get(key: string, defaultValue?: Object) {
    var value = this.storage[this.fullKey(key)];
    if (typeof value === "undefined") return defaultValue;
    return value;
  }

  set(key: string, value: Object) {
    this.storage[this.fullKey(key)] = value;
  }

  fullKey(key: string) {
    return this.prefix + key;
  }
}

export default Storage;
