import { useEffect, useRef, useState } from "react";
import { Button, Card, Input, Progress, Select, Space, Steps, Typography, message } from "antd";
import { api } from "../api";

const STAGES = ["S0_io", "S1_catalog", "S2_at", "S3_dense", "S4_dsm", "S5_ortho", "S6_report"];

export default function ExecutePage() {
  const [profiles, setProfiles] = useState<any[]>([]);
  const [profileId, setProfileId] = useState<number | undefined>();
  const [inputDir, setInputDir] = useState("");
  const [outputDir, setOutputDir] = useState("");
  const [job, setJob] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    api.profiles().then(setProfiles).catch((e) => message.error(String(e)));
  }, []);

  useEffect(() => {
    if (!job?.id) return;
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/ws/jobs/${job.id}`);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.job) setJob((j: any) => ({ ...j, ...msg.job, id: j.id }));
      } catch {
        /* ignore */
      }
    };
    wsRef.current = ws;
    const timer = setInterval(() => {
      api.job(job.id).then(setJob).catch(() => undefined);
    }, 5000);
    return () => {
      ws.close();
      clearInterval(timer);
    };
  }, [job?.id]);

  const stageIdx = Math.max(0, STAGES.indexOf(job?.current_stage || job?.completed_stage || "S0_io"));

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="large">
      <Card title="启动任务">
        <Space direction="vertical" style={{ width: "100%" }}>
          <Select
            placeholder="选择参数模板"
            style={{ width: "100%" }}
            options={profiles.map((p) => ({ value: p.id, label: `${p.name} (v${p.version})` }))}
            value={profileId}
            onChange={setProfileId}
          />
          <Input addonBefore="输入目录" value={inputDir} onChange={(e) => setInputDir(e.target.value)} placeholder="/data/..." />
          <Input addonBefore="输出目录" value={outputDir} onChange={(e) => setOutputDir(e.target.value)} placeholder="/data/runs/..." />
          <Button
            type="primary"
            onClick={async () => {
              try {
                const j = await api.createJob({
                  profile_id: profileId,
                  input_dir: inputDir,
                  output_dir: outputDir,
                  params: {},
                });
                setJob(j);
                message.success("已下发");
              } catch (e: any) {
                message.error(e.message);
              }
            }}
          >
            开始执行
          </Button>
        </Space>
      </Card>

      {job && (
        <Card
          title={`任务 ${job.id} · ${job.status}`}
          extra={
            <Space>
              <Button disabled={job.status !== "running"} onClick={() => api.jobAction(job.id, "pause").then(setJob)}>
                暂停
              </Button>
              <Button disabled={job.status !== "paused"} onClick={() => api.jobAction(job.id, "resume").then(setJob)}>
                恢复
              </Button>
              <Button
                type="primary"
                disabled={job.status !== "awaiting_continue"}
                onClick={() => api.jobAction(job.id, "continue").then(setJob)}
              >
                继续下一阶段
              </Button>
              <Button danger onClick={() => api.jobAction(job.id, "cancel").then(setJob)}>
                取消
              </Button>
            </Space>
          }
        >
          <Steps
            size="small"
            current={stageIdx}
              items={STAGES.map((s) => ({ title: s }))}
              style={{ marginBottom: 16 }}
            />
          <Progress percent={Math.round(job.global_percent || 0)} status={job.status === "failed" ? "exception" : "active"} />
          <Typography.Paragraph>
            {job.message}
            {job.eta_seconds != null ? ` · ETA ${Math.round(job.eta_seconds / 60)} 分钟` : ""}
          </Typography.Paragraph>
          {job.error_summary && <Typography.Text type="danger">{job.error_summary}</Typography.Text>}
        </Card>
      )}
    </Space>
  );
}
