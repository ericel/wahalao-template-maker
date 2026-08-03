import { describe, expect, it } from "vitest";
import { initialDraft, recipePath, validateDraft } from "./template";
import { parseTemplate, serializeTemplate } from "./templateYaml";

describe("template authoring", () => {
  it("round-trips the starter recipe through YAML", () => {
    expect(parseTemplate(serializeTemplate(initialDraft))).toEqual(initialDraft);
  });

  it("builds the upstream registry path", () => {
    expect(recipePath(initialDraft)).toBe("registry/recipes/weynear/new-template/0.1.0");
  });

  it("requires a console-issued submission and real source commit", () => {
    const failed = validateDraft(initialDraft).filter((item) => !item.valid);

    expect(failed.map((item) => item.id)).toEqual(["submission", "source"]);
  });
});
