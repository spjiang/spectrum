import { useEffect, useState } from "react";
import { Button, Card, Table, message } from "antd";
import { api } from "../api";

export default function JobsPage() {
  const [rows, setRows] = useState<any[]>([]);
  async function reload() {
    setRows(await api.jobs());
  }
  useEffect(() => {
    reload().catch((e) => message.error(String(e)));
  }, []);
  return (
    <Card
      title="执行记录"
      extra={
        <Button onClick={() => reload()}>刷新</Button>
      }
    >
      <Table
        rowKey="id"
        dataSource={rows}
        columns={[
          { title: "ID", dataIndex: "id", ellipsis: true },
          { title: "状态", dataIndex: "status", width: 140 },
          { title: "阶段", dataIndex: "current_stage", width: 120 },
          { title: "完成阶段", dataIndex: "completed_stage", width: 120 },
          { title: "进度", dataIndex: "global_percent", width: 80, render: (v) => `${Math.round(v || 0)}%` },
          { title: "输入", dataIndex: "input_dir", ellipsis: true },
          { title: "输出", dataIndex: "output_dir", ellipsis: true },
          {
            title: "操作",
            width: 220,
            render: (_, r) => (
              <>
                <Button
                  size="small"
                  type="link"
                  onClick={() => api.logs(r.id).then((t) => message.info(t.slice(0, 500) || "(空)"))}
                >
                  日志
                </Button>
                <Button size="small" type="link" href={`/api/jobs/${r.id}/report.pdf`} target="_blank">
                  报告
                </Button>
              </>
            ),
          },
        ]}
      />
    </Card>
  );
}
