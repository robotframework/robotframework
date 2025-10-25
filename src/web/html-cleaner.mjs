import { Transformer } from "@parcel/plugin";

// Remove leading whitespace from each line in the template file.
// This is needed for whitespace sensitive templates (e.g preformatted code blocks)
export default new Transformer({
  async transform({ asset }) {
    // Retrieve the asset's source code and source map.
    let source = await asset.getCode();
    // Run it through some compiler, and set the results
    // on the asset.
    let cleaned = "";
    source.split("\n").forEach(line => {
      cleaned += line.trim() + "\n";
    });
    asset.setCode(cleaned);

    // Return the asset
    return [asset];
  }
});