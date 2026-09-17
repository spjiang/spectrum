import type { InjectionKey, Ref } from "vue";
import type { LlmConfig } from "./llmConfig";

/** 壳层把大模型配置注入算法页。 */
export const LLM_CONFIG_KEY: InjectionKey<Ref<LlmConfig>> = Symbol("l3-aide-llm-config");
