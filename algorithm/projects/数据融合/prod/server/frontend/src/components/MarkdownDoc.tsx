import { useMemo, type ReactNode } from "react";
import { Affix, Anchor, Col, Row, Spin, Typography } from "antd";
import type { AnchorLinkItemProps } from "antd/es/anchor/Anchor";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import MermaidBlock from "./MermaidBlock";

function slugify(text: string) {
  return text
    .trim()
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fff\- ]+/g, "")
    .replace(/\s+/g, "-");
}

function headingText(children: ReactNode): string {
  if (children == null || typeof children === "boolean") return "";
  if (typeof children === "string" || typeof children === "number") return String(children);
  if (Array.isArray(children)) return children.map(headingText).join("");
  if (typeof children === "object" && "props" in (children as object)) {
    return headingText((children as { props?: { children?: ReactNode } }).props?.children);
  }
  return "";
}

function stripMd(title: string) {
  return title.replace(/[`*_]/g, "").trim();
}

/** 左侧目录：二级=章/阶段，三级=阶段或参数，四级=参数名。 */
export function markdownToc(md: string): AnchorLinkItemProps[] {
  const items: AnchorLinkItemProps[] = [];
  let inFence = false;
  for (const raw of md.split("\n")) {
    if (raw.trim().startsWith("```")) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;
    const m = /^(#{2,4})\s+(.+)$/.exec(raw);
    if (!m) continue;
    const depth = m[1].length;
    const title = stripMd(m[2]);
    const id = slugify(title);
    const item: AnchorLinkItemProps = { key: `${depth}-${id}`, href: `#${id}`, title };
    if (depth === 2) {
      items.push(item);
      continue;
    }
    const h2 = items[items.length - 1];
    if (!h2) continue;
    const kids = (h2.children ??= []);
    if (depth === 3) {
      kids.push(item);
      continue;
    }
    const h3 = kids[kids.length - 1];
    if (h3) {
      (h3.children ??= []).push(item);
    } else {
      kids.push(item);
    }
  }
  return items;
}

export default function MarkdownDoc({
  md,
  loading,
  intro,
}: {
  md: string;
  loading?: boolean;
  intro?: ReactNode;
}) {
  const body = useMemo(() => md.replace(/^#\s+[^\n]+\n+/, ""), [md]);
  const toc = useMemo(() => markdownToc(body), [body]);

  if (loading) {
    return (
      <div style={{ padding: 48, textAlign: "center" }}>
        <Spin />
      </div>
    );
  }

  return (
    <>
      {intro}
      <Row gutter={24} className="mosaic-cli-doc-row">
        <Col xs={0} md={7}>
          {/* Affix 用 fixed 钉住，不受 ant-layout overflow 影响；纯 sticky 在本壳层会失效 */}
          <Affix offsetTop={64}>
            <div className="mosaic-cli-toc">
              <Typography.Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
                目录
              </Typography.Text>
              <Anchor affix={false} items={toc} />
            </div>
          </Affix>
        </Col>
        <Col xs={24} md={17}>
          <div className="mosaic-markdown">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h2: ({ children, ...props }) => (
                  <h2 id={slugify(headingText(children))} {...props}>
                    {children}
                  </h2>
                ),
                h3: ({ children, ...props }) => (
                  <h3 id={slugify(headingText(children))} {...props}>
                    {children}
                  </h3>
                ),
                h4: ({ children, ...props }) => (
                  <h4 id={slugify(headingText(children))} {...props}>
                    {children}
                  </h4>
                ),
                a: ({ href, children, ...props }) => (
                  <a href={href} target={href?.startsWith("http") ? "_blank" : undefined} rel="noreferrer" {...props}>
                    {children}
                  </a>
                ),
                pre: ({ children }) => <>{children}</>,
                code: ({ className, children, ...props }) => {
                  const lang = /language-(\w+)/.exec(className || "")?.[1];
                  const text = String(children).replace(/\n$/, "");
                  if (lang === "mermaid") return <MermaidBlock chart={text} />;
                  if (lang) {
                    return (
                      <pre>
                        <code className={className} {...props}>
                          {children}
                        </code>
                      </pre>
                    );
                  }
                  return (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {body}
            </ReactMarkdown>
          </div>
        </Col>
      </Row>
    </>
  );
}
