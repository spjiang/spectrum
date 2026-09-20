import { useCallback, useEffect, useMemo, useRef, useState, type Key } from "react";
import { Alert, Button, Card, Col, Popconfirm, Row, Space, Table, Tag, Typography, message } from "antd";
import { ReloadOutlined, StopOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { formatNo } from "../ids";
import JobStatusTag from "../components/JobStatusTag";
import JobStageFlow from "../components/JobStageFlow";
import JobActions from "../components/JobActions";
import { TitleWithProgressHelp } from "../components/ProgressHelpTip";
import { formatJobDateTime, jobElapsedHours } from "../jobTime";
import { attachJobProcesses, fmtMb, jobComputeState, restoreOrphanHierarchy, type Proc } from "../processTree";
import JobProcessTable from "../components/JobProcessTable";

type Memory = {
  worker_rss_mb?: number | null;
  helper_rss_mb?: number | null;
  job_rss_mb?: number | null;
  tree_rss_mb?: number | null;
  container_used_mb?: number | null;
  container_peak_mb?: number | null;
  container_limit_mb?: number | null;
};

type Inspect = {
  status: string;
  alive: boolean;
  heartbeat_age_seconds: number | null;
  heartbeat_path: string;
  queue: string;
  mq_status: string;
  consumers: number | null;
  queued_messages: number | null;
  active_jobs: any[];
  worker: {
    hostname?: string;
    pid?: number;
    python?: string;
    cwd?: string;
    listening?: boolean;
    started_at?: string;
    updated_at?: string;
    current_job?: any;
    thread_count?: number;
    threads?: { name: string; ident?: number | null; daemon: boolean; alive: boolean }[];
    processes?: Proc[];
    memory?: Memory;
    host_memory?: { mem_total_mb?: number | null; mem_available_mb?: number | null };
  } | null;
};

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="mosaic-stat">
      <div className="mosaic-stat-label">{label}</div>
      <div className="mosaic-stat-value" style={{ fontSize: 16 }}>
        {value}
      </div>
    </div>
  );
}

function mergeCurrentRows(current: any, activeJobs: any[]) {
  const leftover = new Map(activeJobs.map((j) => [String(j.id), j]));
  const rows: any[] = [];
  if (current?.job_id) {
    const id = String(current.job_id);
    const db = leftover.get(id) || {};
    leftover.delete(id);
    rows.push({
      key: id,
      id,
      seq: db.seq,
      status: db.status || "running",
      current_stage: db.current_stage,
      completed_stage: db.completed_stage,
      global_percent: db.global_percent,
      message: db.message,
      input_dir: current.input_dir || db.input_dir,
      output_dir: current.output_dir || db.output_dir,
      pid: current.pid,
      started_at: current.started_at || db.started_at,
      created_at: db.created_at,
      finished_at: db.finished_at,
      source: "worker",
    });
  }
  for (const j of leftover.values()) {
    rows.push({
      ...j,
      key: String(j.id),
      id: String(j.id),
      source: "db",
    });
  }
  return rows;
}

function memoryOf(w: Inspect["worker"]): Memory {
  if (w?.memory && (w.memory.tree_rss_mb != null || w.memory.worker_rss_mb != null)) {
    return w.memory;
  }
  const procs = w?.processes || [];
  const root = w?.pid;
  let worker = 0;
  let helper = 0;
  let job = 0;
  for (const p of procs) {
    const rss = p.rss_mb || 0;
    if (p.pid === root) worker = rss;
    else if (String(p.cmdline || "").includes("resource_tracker")) helper += rss;
    else job += rss;
  }
  return {
    worker_rss_mb: worker,
    helper_rss_mb: helper,
    job_rss_mb: job,
    tree_rss_mb: Number((worker + helper + job).toFixed(1)),
  };
}

export default function WorkerPage() {
  const [data, setData] = useState<Inspect | null>(null);
  const [loading, setLoading] = useState(true);
  const [killing, setKilling] = useState(false);
  const [openJobs, setOpenJobs] = useState<Key[]>([]);
  const seenJobs = useRef(new Set<string>());
  const nav = useNavigate();

  const reload = useCallback(async () => {
    setData(await api.workerInspect());
  }, []);

  useEffect(() => {
    let alive = true;
    let busy = false;
    const tick = async () => {
      if (!alive || busy || document.hidden) return;
      busy = true;
      try {
        const next = await api.workerInspect();
        if (alive) {
          setData(next);
          setLoading(false);
        }
      } catch (e: any) {
        if (alive) {
          setLoading(false);
          message.error(String(e.message || e));
        }
      } finally {
        busy = false;
      }
    };
    tick();
    const t = setInterval(tick, 4000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const w = data?.worker;
  const alive = !!data?.alive;
  const current = w?.current_job;
  const activeJobs = data?.active_jobs || [];
  const mem = memoryOf(w);
  const processRows = useMemo(() => restoreOrphanHierarchy(w?.processes || [], w?.pid), [w?.processes, w?.pid]);
  const currentRows = useMemo(() => {
    const rows = mergeCurrentRows(current, activeJobs);
    return rows.map((r) => {
      const attached = attachJobProcesses(r, data);
      const compute_state = jobComputeState(r, data);
      const live = attached.process_count > 0;
      return {
        ...r,
        ...attached,
        compute_state,
        source: r.source === "db" && live ? "worker" : r.source,
      };
    });
  }, [current, activeJobs, data]);
  const stuckRows = currentRows.filter((r) => r.compute_state === "orphan" || r.compute_state === "stale");
  useEffect(() => {
    const extra: Key[] = [];
    for (const r of currentRows) {
      const key = String(r.key);
      if ((r.processes || []).length && !seenJobs.current.has(key)) {
        seenJobs.current.add(key);
        extra.push(key);
      }
    }
    if (extra.length) setOpenJobs((prev) => [...prev, ...extra]);
  }, [currentRows]);
  const queueOk = data?.mq_status === "ok" || (alive && !!w?.listening);
  const queueText = data?.mq_status === "ok" ? "已监听" : alive && w?.listening ? "Worker 在消费" : data?.mq_status || "未知";

  async function onKillAll() {
    setKilling(true);
    try {
      const r = await api.killAllWorkerJobs();
      message.success(r.killed ? `已杀死 ${r.killed} 条任务，Worker 计算进程已停止` : "已发出杀死指令，Worker 计算进程已停止");
      await reload();
    } catch (e: any) {
      message.error(e.message);
    } finally {
      setKilling(false);
    }
  }

  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <Card
        className="mosaic-panel"
        title="Worker 服务"
        extra={
          <Button icon={<ReloadOutlined />} loading={loading} onClick={() => reload().catch((e) => message.error(String(e)))}>
            刷新
          </Button>
        }
      >
        <Typography.Paragraph type="secondary" style={{ marginBottom: 16 }}>
          「在线」来自心跳文件（进程还在写盘）。「队列」是 RabbitMQ 上 mosaic.jobs 登记的消费者数。Worker 在跑长任务时登记可能暂时为 0，只要心跳在线且正在消费，任务仍会继续。
        </Typography.Paragraph>
        <Space wrap style={{ marginBottom: 16 }}>
          <Tag color={alive ? "success" : "error"}>{alive ? "在线" : "离线"}</Tag>
          <Tag color={queueOk ? "success" : "warning"}>队列 {queueText}</Tag>
          {w?.listening ? <Tag>{data?.queue}</Tag> : null}
        </Space>
        <Row gutter={[12, 12]}>
          <Col xs={12} md={6}>
            <Stat label="主机" value={w?.hostname || "—"} />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="主进程 PID" value={w?.pid != null ? String(w.pid) : "—"} />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="消费者 / 排队" value={`${data?.consumers ?? "—"} / ${data?.queued_messages ?? "—"}`} />
          </Col>
          <Col xs={12} md={6}>
            <Stat
              label="心跳延迟"
              value={data?.heartbeat_age_seconds != null ? `${data.heartbeat_age_seconds}s` : "无心跳"}
            />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="Worker 自身" value={fmtMb(mem.worker_rss_mb)} />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="任务进程" value={fmtMb(mem.job_rss_mb ?? 0)} />
          </Col>
        </Row>
        <Typography.Paragraph type="secondary" style={{ marginTop: 12, marginBottom: 0, fontSize: 12 }}>
          Python {w?.python || "—"} · cwd {w?.cwd || "—"} · {data?.heartbeat_path}
        </Typography.Paragraph>
      </Card>

      <Card
        className="mosaic-panel"
        title="当前任务"
        extra={
          <Popconfirm
            title="杀死全部任务？"
            description="会立刻停掉计算并取消未结束任务，不能再续跑。进度卡住请用任务上的「清理并续跑」。"
            okText="杀死全部"
            okButtonProps={{ danger: true }}
            onConfirm={onKillAll}
          >
            <Button danger icon={<StopOutlined />} loading={killing}>
              杀死全部任务
            </Button>
          </Popconfirm>
        }
      >
        {stuckRows.some((r) => r.compute_state === "orphan") && (
          <Alert
            type="warning"
            showIcon
            style={{ marginBottom: 12 }}
            message="包装进程已退出，计算子进程还挂着，进度不会再往前走"
            description="点该任务的「清理并续跑」：清掉空转进程，有 DSM 就从正射接着跑。不要点「杀死全部任务」，那会变成已取消。"
          />
        )}
        {stuckRows.some((r) => r.compute_state === "stale") && !stuckRows.some((r) => r.compute_state === "orphan") && (
          <Alert
            type="warning"
            showIcon
            style={{ marginBottom: 12 }}
            message="库里仍显示未结束，Worker 没有对应计算"
            description="点该任务的「清理并续跑」。只有确定要放弃这次成果时，才用「杀死全部任务」。"
          />
        )}
        <Table
          size="small"
          rowKey="key"
          pagination={false}
          scroll={{ x: 1280 }}
          dataSource={currentRows}
          locale={{ emptyText: "Worker 空闲，没有正在计算的任务。" }}
          expandable={{
            expandedRowKeys: openJobs,
            onExpandedRowsChange: (keys) => setOpenJobs([...keys]),
            rowExpandable: (r) => (r.processes || []).length > 0,
            expandedRowRender: (r) => <JobProcessTable processes={r.processes || []} />,
          }}
          columns={[
            {
              title: "任务号",
              dataIndex: "seq",
              width: 88,
              render: (v, r) => <Typography.Text strong>{formatNo(v, r.id ? String(r.id).slice(0, 8) : "—")}</Typography.Text>,
            },
            {
              title: "来源",
              dataIndex: "source",
              width: 100,
              render: (v, r) =>
                r.compute_state === "orphan" ? (
                  <Tag color="orange">已脱离</Tag>
                ) : v === "worker" || r.compute_state === "live" ? (
                  <Tag color="blue">计算中</Tag>
                ) : (
                  <Tag>仅库记录</Tag>
                ),
            },
            {
              title: "状态",
              dataIndex: "status",
              width: 110,
              render: (v) => <JobStatusTag status={v} />,
            },
            {
              title: <TitleWithProgressHelp>进度</TitleWithProgressHelp>,
              dataIndex: "global_percent",
              width: 96,
              render: (v) => `${Math.round(v || 0)}%`,
            },
            {
              title: "流程",
              width: 220,
              render: (_, r) => <JobStageFlow job={r} variant="compact" />,
            },
            {
              title: "进程",
              dataIndex: "process_count",
              width: 140,
              render: (v, r) => (v ? `${v} 个 / ${fmtMb(r.process_rss_mb)}` : "—"),
            },
            {
              title: "开始时间",
              dataIndex: "started_at",
              width: 170,
              render: (v) => formatJobDateTime(v),
            },
            {
              title: "结束时间",
              dataIndex: "finished_at",
              width: 170,
              render: (v) => formatJobDateTime(v),
            },
            {
              title: "总耗时",
              width: 110,
              render: (_, r) => jobElapsedHours(r),
            },
            {
              title: "输入",
              dataIndex: "input_dir",
              ellipsis: true,
              render: (v) => (v ? <Typography.Text copyable={{ text: v }}>{v}</Typography.Text> : "—"),
            },
            {
              title: "输出",
              dataIndex: "output_dir",
              ellipsis: true,
              render: (v) => (v ? <Typography.Text copyable={{ text: v }}>{v}</Typography.Text> : "—"),
            },
            {
              title: "说明",
              dataIndex: "message",
              ellipsis: true,
              render: (v) => v || "—",
            },
            {
              title: "操作",
              width: 220,
              render: (_, r) => (
                <Space wrap size={4}>
                  <JobActions job={r} inspect={data} computeState={r.compute_state} onChanged={() => reload()} />
                  <Button type="link" size="small" onClick={() => nav(`/execute?job=${r.id}`)}>
                    监控
                  </Button>
                </Space>
              ),
            },
          ]}
        />
      </Card>

      <Card className="mosaic-panel" title="内存占用">
        <Typography.Paragraph type="secondary" style={{ marginBottom: 16 }}>
          没有任务时「任务进程」为 0 MB，这里仍会显示 Worker 自身和容器占用，方便对比空闲基线。Worker 容器不设内存上限。
        </Typography.Paragraph>
        <Row gutter={[12, 12]}>
          <Col xs={12} md={6}>
            <Stat label="Worker 自身" value={fmtMb(mem.worker_rss_mb)} />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="任务进程" value={fmtMb(mem.job_rss_mb ?? 0)} />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="辅助进程" value={fmtMb(mem.helper_rss_mb ?? 0)} />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="进程树合计" value={fmtMb(mem.tree_rss_mb)} />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="容器已用" value={fmtMb(mem.container_used_mb)} />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="容器峰值" value={fmtMb(mem.container_peak_mb)} />
          </Col>
          <Col xs={12} md={6}>
            <Stat
              label="容器限额"
              value={mem.container_limit_mb == null ? "不限制" : fmtMb(mem.container_limit_mb)}
            />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="引擎可见总量" value={fmtMb(w?.host_memory?.mem_total_mb)} />
          </Col>
          <Col xs={12} md={6}>
            <Stat label="引擎当前空闲" value={fmtMb(w?.host_memory?.mem_available_mb)} />
          </Col>
        </Row>
        <Typography.Paragraph type="secondary" style={{ marginTop: 12, marginBottom: 0, fontSize: 12 }}>
          引擎可见总量是 Docker 分配给 Linux 虚拟机的内存，不是 macOS 宿主机全部内存。要用 36GB 任务预算，请把 Docker Desktop → Settings → Resources → Memory 调到 ≥ 36GB。
        </Typography.Paragraph>
      </Card>

      <Card className="mosaic-panel" title="全部进程">
        <Typography.Paragraph type="secondary" style={{ marginBottom: 12 }}>
          按父子关系列出容器内全部进程（含任务进程池拉起的子进程 / 孙进程）。缩进表示层级，展开可看该进程的 Linux 线程。
        </Typography.Paragraph>
        <Table
          size="small"
          rowKey="pid"
          pagination={false}
          dataSource={processRows}
          locale={{ emptyText: alive ? "暂无进程信息" : "Worker 未上报进程" }}
          expandable={{
            rowExpandable: (r) => !r.synthetic && ((r.tasks && r.tasks.length > 0) || (r.threads || 0) > 1),
            expandedRowRender: (r) => (
              <Table
                size="small"
                rowKey="tid"
                pagination={false}
                dataSource={
                  r.tasks && r.tasks.length
                    ? r.tasks
                    : Array.from({ length: r.threads || 0 }, (_, i) => ({
                        tid: i === 0 ? r.pid : `${r.pid}-${i}`,
                        comm: i === 0 ? (r.comm || "main") : `thread-${i}`,
                        state: "—",
                        main: i === 0,
                      }))
                }
                columns={[
                  { title: "TID", dataIndex: "tid", width: 110 },
                  { title: "名称", dataIndex: "comm" },
                  { title: "状态", dataIndex: "state", width: 80 },
                  {
                    title: "角色",
                    dataIndex: "main",
                    width: 90,
                    render: (v: boolean) => (v ? "主线程" : "子线程"),
                  },
                ]}
              />
            ),
          }}
          columns={[
            { title: "PID", dataIndex: "pid", width: 80, render: (v, r) => (r.synthetic ? "—" : v) },
            { title: "PPID", dataIndex: "ppid", width: 80, render: (v, r) => (r.synthetic ? "—" : v ?? "—") },
            {
              title: "子进程",
              dataIndex: "child_count",
              width: 80,
              render: (v) => v || 0,
            },
            { title: "状态", dataIndex: "state", width: 70, render: (v) => v || "—" },
            { title: "线程", dataIndex: "threads", width: 70, render: (v, r) => (r.synthetic ? "—" : v ?? "—") },
            {
              title: "RSS",
              dataIndex: "rss_mb",
              width: 90,
              render: (v) => (v == null ? "—" : `${v} MB`),
            },
            {
              title: "命令行",
              dataIndex: "cmdline",
              ellipsis: true,
              render: (v, r) => (
                <span style={{ paddingLeft: (r.depth || 0) * 18 }}>
                  {(r.depth || 0) > 0 ? "↳ " : ""}
                  {r.synthetic ? <Typography.Text type="secondary">{v}</Typography.Text> : v || "—"}
                </span>
              ),
            },
          ]}
        />
      </Card>

      <Card className="mosaic-panel" title="Worker 主进程线程">
        <Table
          size="small"
          rowKey={(r) => `${r.name}-${r.ident ?? ""}`}
          pagination={false}
          dataSource={w?.threads || []}
          locale={{ emptyText: "暂无线程信息" }}
          columns={[
            { title: "名称", dataIndex: "name" },
            {
              title: "守护",
              dataIndex: "daemon",
              width: 80,
              render: (v) => (v ? "是" : "否"),
            },
            {
              title: "存活",
              dataIndex: "alive",
              width: 80,
              render: (v) => (v ? "是" : "否"),
            },
          ]}
        />
      </Card>
    </Space>
  );
}
