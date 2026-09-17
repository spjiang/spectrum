/** 本机保存的按算法提示词，只放 localStorage，不写仓库。 */

export interface PromptOverride {
  system: string;
  user: string;
}

const STORAGE_KEY = "l3-aide-prompt-overrides";

function readAll(): Record<string, PromptOverride> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<string, PromptOverride>;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

export function loadPromptOverride(algorithmId: string): PromptOverride | null {
  const row = readAll()[algorithmId];
  if (!row) return null;
  const system = typeof row.system === "string" ? row.system : "";
  const user = typeof row.user === "string" ? row.user : "";
  if (!system.trim() && !user.trim()) return null;
  return { system, user };
}

export function savePromptOverride(algorithmId: string, prompt: PromptOverride): void {
  const all = readAll();
  all[algorithmId] = {
    system: prompt.system,
    user: prompt.user,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
}

export function clearPromptOverride(algorithmId: string): void {
  const all = readAll();
  delete all[algorithmId];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
}
