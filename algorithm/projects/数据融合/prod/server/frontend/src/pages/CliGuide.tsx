import { useEffect, useState } from "react";
import { Card, Typography, message } from "antd";
import { api } from "../api";
import MarkdownDoc from "../components/MarkdownDoc";

const TABS = [
  { key: "cli", tab: "命令行手册" },
  { key: "params", tab: "参数说明" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export default function CliGuidePage() {
  const [tab, setTab] = useState<TabKey>("params");
  const [cliMd, setCliMd] = useState("");
  const [paramMd, setParamMd] = useState("");
  const [cliLoading, setCliLoading] = useState(true);
  const [paramLoading, setParamLoading] = useState(true);

  useEffect(() => {
    api
      .cliGuide()
      .then(setCliMd)
      .catch((e) => message.error(String(e)))
      .finally(() => setCliLoading(false));
    api
      .paramGuide()
      .then(setParamMd)
      .catch((e) => message.error(String(e)))
      .finally(() => setParamLoading(false));
  }, []);

  return (
    <Card
      className="mosaic-panel mosaic-cli-guide"
      tabList={[...TABS]}
      activeTabKey={tab}
      onTabChange={(key) => setTab(key as TabKey)}
    >
      {tab === "cli" ? (
        <MarkdownDoc
          md={cliMd}
          loading={cliLoading}
          intro={
            <Typography.Paragraph type="secondary" style={{ marginBottom: 16 }}>
              ① 部署安装 → ② 命令行参数 → ③ 本机测区示例。相对路径均相对主程序安装目录。
            </Typography.Paragraph>
          }
        />
      ) : (
        <MarkdownDoc
          md={paramMd}
          loading={paramLoading}
          intro={
            <Typography.Paragraph type="secondary" style={{ marginBottom: 16 }}>
              按进度条节点说明算法与处理方案参数。改大、改小、关闭的效果写在各表最后两列。
            </Typography.Paragraph>
          }
        />
      )}
    </Card>
  );
}
