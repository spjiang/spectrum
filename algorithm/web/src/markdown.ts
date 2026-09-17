/** 把大模型 Markdown 转成可安全插入页面的 HTML。 */

import { marked } from "marked";
import DOMPurify from "dompurify";

marked.setOptions({
  gfm: true,
  breaks: true,
});

export function renderMarkdown(source: string): string {
  const html = marked.parse(source.trim() || "", { async: false }) as string;
  if (typeof globalThis.window === "undefined") {
    return html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, "");
  }
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
}
