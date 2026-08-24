/** 业务层级：汉字为主，L0/L1 仅作备注。名称表示「进组干什么」。 */
export const GROUP_ORDER = ["L0前", "L0", "L0→L1", "L1", "L1→L2", "L2", "L3", "L3→L4", "L4"] as const;

export const GROUP_LABEL: Record<string, string> = {
  L0前: "航线规划",
  L0: "采集质检",
  "L0→L1": "辐射校正",
  L1: "相对归一",
  "L1→L2": "反射率与正射",
  L2: "镶嵌与特征",
  L3: "指数与识别",
  "L3→L4": "图斑整理",
  L4: "地块汇总",
};

export function groupTitle(level: string): string {
  return GROUP_LABEL[level] || level;
}

export function groupNote(level: string): string {
  return level;
}
