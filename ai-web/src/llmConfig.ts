/** 本机大模型调试配置，密钥只放 localStorage。 */

export interface LlmConfig {
  enabled: boolean;
  baseUrl: string;
  model: string;
  apiKey: string;
}

const STORAGE_KEY = "l3-aide-llm-config";

export const defaultLlmConfig = (): LlmConfig => ({
  enabled: false,
  baseUrl: "https://api.deepseek.com",
  model: "deepseek-chat",
  apiKey: "",
});

export function loadLlmConfig(): LlmConfig {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultLlmConfig();
    const parsed = JSON.parse(raw) as Partial<LlmConfig>;
    return {
      ...defaultLlmConfig(),
      ...parsed,
      apiKey: typeof parsed.apiKey === "string" ? parsed.apiKey : "",
    };
  } catch {
    return defaultLlmConfig();
  }
}

export function saveLlmConfig(config: LlmConfig): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

export function llmRequestBody(config: LlmConfig): { baseUrl: string; model: string; apiKey: string } | undefined {
  if (!config.enabled || !config.apiKey.trim()) return undefined;
  return {
    baseUrl: config.baseUrl.trim() || "https://api.deepseek.com",
    model: config.model.trim() || "deepseek-chat",
    apiKey: config.apiKey.trim(),
  };
}
