import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { renderMarkdown } from "../.tmp-md-test/markdown.js";

describe("renderMarkdown", () => {
  it("renders headings lists and emphasis", () => {
    const html = renderMarkdown("## 结论\n\n- **均值**合理\n- 不是处方");
    assert.match(html, /<h2>/);
    assert.match(html, /<li>/);
    assert.match(html, /<strong>/);
  });

  it("strips script tags", () => {
    const html = renderMarkdown('<script>alert(1)</script>正常');
    assert.doesNotMatch(html, /<script/i);
  });
});
