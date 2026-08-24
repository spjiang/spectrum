import type { AlgoWayhoDoc } from "./types";
import { L0_WAYHO } from "./l0";
import { L2_WAYHO } from "./l2";
import { L3_WAYHO } from "./l3";

const ALL: AlgoWayhoDoc[] = [...L0_WAYHO, ...L2_WAYHO, ...L3_WAYHO];
const BY_ID = new Map(ALL.map((d) => [d.id, d]));

export function getWayhoAnalysis(id: string): AlgoWayhoDoc | undefined {
  return BY_ID.get(id);
}

export function wayhoAnalysisCount(): number {
  return ALL.length;
}
