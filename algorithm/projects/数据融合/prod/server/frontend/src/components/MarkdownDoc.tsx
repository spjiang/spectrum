import { useMemo, type ReactNode } from "react";
import { Anchor, Col, Row, Spin, Typography } from "antd";
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

function headingText(children: ReactNode) {
  return String(children ?? "");
}

export function markdownToc(md: string) {
  return md
    .split("\n")
    .filter((line) => line.startsWith("## "))
    .map((line) => {
      const title = line.replace(/^##\s+/, "").trim();
      return { key: slugify(title), href: `#${slugify(title)}`, title };
    });
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
      <Row gutter={24}>
        <Col xs={0} md={5}>
          <div className="mosaic-cli-toc">
            <Typography.Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
              目录
            </Typography.Text>
            <Anchor affix={false} offsetTop={88} items={toc} />
          </div>
        </Col>
        <Col xs={24} md={19}>
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
