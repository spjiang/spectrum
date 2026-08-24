import type { PrincipleDoc } from "./types";
import { L0_PRINCIPLES } from "./l0";
import { L2_PRINCIPLES } from "./l2";
import { L3_PRINCIPLES } from "./l3";

const ALL: PrincipleDoc[] = [...L0_PRINCIPLES, ...L2_PRINCIPLES, ...L3_PRINCIPLES];
const BY_ID = new Map(ALL.map((d) => [d.id, d]));

export function getPrinciple(id: string): PrincipleDoc | undefined {
  return BY_ID.get(id);
}

export function hasPrinciple(id: string): boolean {
  return BY_ID.has(id);
}
