/** 人工核实通过的算法。按侧栏标题右侧打勾展示。 */
export const VERIFIED_ALGORITHM_IDS = new Set<string>([
  "27_ndvi",
  "28_ndre",
  "29_evi_savi",
  "30_ndmi_ndwi",
  "31_red_edge_params",
  "32_regression_inversion",
  "33_physical_inversion",
  "34_svm_rf_classify",
  "35_spectral_matching",
]);

export function isAlgorithmVerified(id: string): boolean {
  return VERIFIED_ALGORITHM_IDS.has(id);
}
