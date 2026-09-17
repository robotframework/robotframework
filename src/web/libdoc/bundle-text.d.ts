/**
 * Parcel inlines the content of a file imported with this scheme as a string.
 * TypeScript has no built-in type for it, so without this declaration every
 * type check and every test importing such a module fails with TS2307.
 */
declare module "bundle-text:*" {
  const content: string;
  export default content;
}
