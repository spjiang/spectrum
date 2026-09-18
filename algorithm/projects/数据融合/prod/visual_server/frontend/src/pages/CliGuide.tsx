import { useEffect, useState } from "react";
import { Card, Spin, Typography, message } from "antd";
import ReactMarkdown from "react-markdown";
import { api } from "../api";

export default function CliGuidePage() {
  const [md, setMd] = useState("");
  useEffect(() => {
    api
      .cliGuide()
      .then(setMd)
      .catch((e) => message.error(String(e)));
  }, []);
  return (
    <Card title="命令行使用教学（可不部署可视化服务）">
      <Typography.Paragraph type="secondary">
        以下内容与 source/docs/cli-usage.md 同源，便于项目现场直接 CLI 运行。
      </Typography.Paragraph>
      {md ? <ReactMarkdown>{md}</ReactMarkdown> : <Spin />}
    </Card>
  );
}
