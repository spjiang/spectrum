import { useEffect, useMemo, useState } from "react";
import { Button, Card, Collapse, Form, Input, Select, Space, Switch, Typography, message } from "antd";
import { api } from "../api";

const STAGES = ["S0_io", "S1_catalog", "S2_at", "S3_dense", "S4_dsm", "S5_ortho", "S6_report"];

export default function ProfilesPage() {
  const [defs, setDefs] = useState<any[]>([]);
  const [profiles, setProfiles] = useState<any[]>([]);
  const [name, setName] = useState("默认生产模板");
  const [values, setValues] = useState<Record<string, any>>({});

  const grouped = useMemo(() => {
    const g: Record<string, any[]> = {};
    for (const d of defs) {
      (g[d.stage_id] ||= []).push(d);
    }
    return g;
  }, [defs]);

  async function reload() {
    const [d, p] = await Promise.all([api.paramDefs(), api.profiles()]);
    setDefs(d);
    setProfiles(p);
    const init: Record<string, any> = {};
    for (const x of d) init[x.key] = x.default_value;
    setValues((v) => ({ ...init, ...v }));
  }

  useEffect(() => {
    reload().catch((e) => message.error(String(e)));
  }, []);

  function applyRgbPreset() {
    setValues((v) => ({
      ...v,
      preset: "rgb_preview",
      bands: ["Color"],
      run_mode: "full",
    }));
    message.success("已应用「仅 RGB 快速预览」预设");
  }

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="large">
      <Card
        title="参数配置（按阶段）"
        extra={
          <Space>
            <Button onClick={applyRgbPreset}>仅 RGB 快速预览</Button>
            <Button
              type="primary"
              onClick={async () => {
                try {
                  await api.createProfile({ name, description: "", values, preset: values.preset || null });
                  message.success("已保存模板");
                  await reload();
                } catch (e: any) {
                  message.error(e.message);
                }
              }}
            >
              保存为模板
            </Button>
          </Space>
        }
      >
        <Form layout="vertical">
          <Form.Item label="模板名称">
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </Form.Item>
          <Collapse
            defaultActiveKey={STAGES}
            items={STAGES.filter((s) => grouped[s]).map((stage) => ({
              key: stage,
              label: `阶段 ${stage}`,
              children: (
                <Space direction="vertical" style={{ width: "100%" }}>
                  {(grouped[stage] || []).map((d) => (
                    <div key={d.key}>
                      <Typography.Text strong>{d.key}</Typography.Text>
                      <Typography.Paragraph type="secondary" style={{ marginBottom: 4 }}>
                        {d.description}
                      </Typography.Paragraph>
                      {d.value_type === "bool" ? (
                        <Switch
                          checked={!!values[d.key]}
                          onChange={(c) => setValues({ ...values, [d.key]: c })}
                        />
                      ) : d.key === "run_mode" ? (
                        <Select
                          style={{ width: 280 }}
                          value={values[d.key] || "full"}
                          options={[
                            { value: "full", label: "full 全流程" },
                            { value: "until_stage", label: "until_stage 跑到指定阶段" },
                            { value: "step", label: "step 逐步确认" },
                          ]}
                          onChange={(v) => setValues({ ...values, [d.key]: v })}
                        />
                      ) : d.key === "bands" ? (
                        <Select
                          mode="tags"
                          style={{ width: "100%" }}
                          value={values[d.key] || []}
                          onChange={(v) => setValues({ ...values, [d.key]: v })}
                        />
                      ) : (
                        <Input
                          value={values[d.key] ?? ""}
                          onChange={(e) => {
                            const raw = e.target.value;
                            let parsed: any = raw;
                            if (d.value_type === "int" || d.value_type === "float") {
                              parsed = raw === "" ? null : Number(raw);
                            }
                            setValues({ ...values, [d.key]: parsed });
                          }}
                        />
                      )}
                    </div>
                  ))}
                </Space>
              ),
            }))}
          />
        </Form>
      </Card>
      <Card title="已保存模板">
        {profiles.map((p) => (
          <div key={p.id}>
            #{p.id} {p.name} v{p.version} {p.preset ? `(${p.preset})` : ""}
          </div>
        ))}
      </Card>
    </Space>
  );
}
