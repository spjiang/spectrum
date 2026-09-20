import { Popover } from "antd";
import {
  STAGE_META,
  STAGES,
  activeStageIndex,
  stageLabel,
  toneForStage,
  type JobStageLike,
  type StageId,
} from "../stages";

const TONE_TEXT: Record<string, string> = {
  wait: "未开始",
  process: "进行中",
  finish: "已完成",
  error: "失败",
  pause: "已暂停",
};

function StageNodes({ job, variant }: { job: JobStageLike; variant: "full" | "compact" }) {
  return (
    <div className={`job-stage-flow is-${variant}`} role="list" aria-label="流程节点">
      {STAGES.map((stage, i) => {
        const meta = STAGE_META[stage as StageId];
        const tone = toneForStage(job, stage as StageId);
        return (
          <div key={stage} className="job-stage-item" role="listitem">
            {i > 0 && <div className={`job-stage-line is-${tone}`} />}
            <div className={`job-stage-node is-${tone}`} title={`${meta.label} · ${TONE_TEXT[tone]} · ${meta.hint}`}>
              <span className="job-stage-index">{i}</span>
              <span className="job-stage-name">{variant === "compact" ? meta.short : meta.label}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function summary(job: JobStageLike) {
  const idx = activeStageIndex(job);
  if (idx < 0) {
    return { index: "—", label: job.status === "queued" ? "排队中" : "未开始", tone: "wait" as const };
  }
  const id = STAGES[idx] as StageId;
  return {
    index: String(idx),
    label: STAGE_META[id].label,
    tone: toneForStage(job, id),
  };
}

export default function JobStageFlow({
  job,
  variant = "full",
}: {
  job: JobStageLike;
  variant?: "full" | "compact";
}) {
  if (variant !== "compact") {
    return <StageNodes job={job} variant="full" />;
  }

  const s = summary(job);
  return (
    <Popover
      trigger="click"
      placement="bottomLeft"
      title="流程节点"
      destroyTooltipOnHide
      getPopupContainer={() => document.body}
      content={<StageNodes job={job} variant="full" />}
    >
      <button type="button" className="job-stage-summary" onClick={(e) => e.stopPropagation()}>
        <span className={`job-stage-index is-${s.tone}`}>{s.index}</span>
        <span className="job-stage-summary-label">{s.label}</span>
        <span className={`job-stage-summary-tone is-${s.tone}`}>{TONE_TEXT[s.tone]}</span>
        <span className="job-stage-summary-more">详情</span>
      </button>
    </Popover>
  );
}

export function JobStageCaption({ job }: { job: JobStageLike }) {
  return <span>{stageLabel(job.current_stage || job.completed_stage)}</span>;
}
