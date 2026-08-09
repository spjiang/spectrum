#!/usr/bin/env bash
# 45 算法接口冒烟：在 algorithm/source 下执行
set -euo pipefail
HOST="${HOST:-http://127.0.0.1:28800}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
pass=0; fail=0; skip=0
echo "HOST=$HOST"

echo "=== 01_flight_planning ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/01_flight_planning/run" \
  -F "file=@algorithms/01_flight_planning/testdata/input.geojson" \
  -F 'params={"cruise_speed_m_s":8}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 02_sync_timestamp ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/02_sync_timestamp/run" \
  -F "file=@algorithms/02_sync_timestamp/testdata/input.json" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 03_pos_solution ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/03_pos_solution/run" \
  -F "file=@algorithms/03_pos_solution/testdata/input.csv" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 04_flight_qc ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/04_flight_qc/run" \
  -F "file=@algorithms/04_flight_qc/testdata/input.tif" \
  -F 'params={"max_saturated_ratio":0.01}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 05_cloud_shadow ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/05_cloud_shadow/run" \
  -F "file=@algorithms/05_cloud_shadow/testdata/input.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 06_dark_current ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/06_dark_current/run" \
  -F "file=@algorithms/06_dark_current/testdata/input.tif" \
  -F "file2=@algorithms/06_dark_current/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 07_bad_pixel ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/07_bad_pixel/run" \
  -F "file=@algorithms/07_bad_pixel/testdata/input.tif" \
  -F "file2=@algorithms/07_bad_pixel/testdata/file2.json" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 08_destriping ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/08_destriping/run" \
  -F "file=@algorithms/08_destriping/testdata/input.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 09_smile_keystone ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/09_smile_keystone/run" \
  -F "file=@algorithms/09_smile_keystone/testdata/input.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 10_radiance_calibration ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/10_radiance_calibration/run" \
  -F "file=@algorithms/10_radiance_calibration/testdata/input.tif" \
  -F 'params={"gain":0.01,"offset":0.0}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 11_relative_radiometric ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/11_relative_radiometric/run" \
  -F "file=@algorithms/11_relative_radiometric/testdata/input.tif" \
  -F "file2=@algorithms/11_relative_radiometric/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 12_panel_reflectance ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/12_panel_reflectance/run" \
  -F "file=@algorithms/12_panel_reflectance/testdata/input.tif" \
  -F 'params={"scale":0.001}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 13_atmospheric_correction ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/13_atmospheric_correction/run" \
  -F "file=@algorithms/13_atmospheric_correction/testdata/input.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 14_brdf_correction ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/14_brdf_correction/run" \
  -F "file=@algorithms/14_brdf_correction/testdata/input.tif" \
  -F 'params={"solar_zenith":30,"view_zenith":10}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 15_geo_locate ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/15_geo_locate/run" \
  -F "file=@algorithms/15_geo_locate/testdata/input.tif" \
  -F "file2=@algorithms/15_geo_locate/testdata/file2.json" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 16_orthorectify ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/16_orthorectify/run" \
  -F "file=@algorithms/16_orthorectify/testdata/input.tif" \
  -F "file2=@algorithms/16_orthorectify/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 17_mosaic ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/17_mosaic/run" \
  -F "file=@algorithms/17_mosaic/testdata/input.tif" \
  -F "file2=@algorithms/17_mosaic/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 18_color_balance ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/18_color_balance/run" \
  -F "file=@algorithms/18_color_balance/testdata/input.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 19_multi_source_register ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/19_multi_source_register/run" \
  -F "file=@algorithms/19_multi_source_register/testdata/input.tif" \
  -F "file2=@algorithms/19_multi_source_register/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 20_bad_band_remove ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/20_bad_band_remove/run" \
  -F "file=@algorithms/20_bad_band_remove/testdata/input.tif" \
  -F 'params={"drop_bands":[0,5]}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 21_savgol_smooth ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/21_savgol_smooth/run" \
  -F "file=@algorithms/21_savgol_smooth/testdata/input.tif" \
  -F 'params={"window_length":5,"polyorder":2}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 22_normalize ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/22_normalize/run" \
  -F "file=@algorithms/22_normalize/testdata/input.tif" \
  -F 'params={"method":"zscore"}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 23_pca ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/23_pca/run" \
  -F "file=@algorithms/23_pca/testdata/input.tif" \
  -F 'params={"n_components":3}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 24_band_select ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/24_band_select/run" \
  -F "file=@algorithms/24_band_select/testdata/input.tif" \
  -F "file2=@algorithms/24_band_select/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 25_superpixel ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/25_superpixel/run" \
  -F "file=@algorithms/25_superpixel/testdata/input.tif" \
  -F 'params={"n_segments":20}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 26_patch_build ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/26_patch_build/run" \
  -F "file=@algorithms/26_patch_build/testdata/input.tif" \
  -F "file2=@algorithms/26_patch_build/testdata/file2.tif" \
  -F 'params={"patch_size":5}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 27_ndvi ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/27_ndvi/run" \
  -F "file=@algorithms/27_ndvi/testdata/input.tif" \
  -F 'params={"red_band":2,"nir_band":3}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 28_ndre ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/28_ndre/run" \
  -F "file=@algorithms/28_ndre/testdata/input.tif" \
  -F 'params={"re_band":4,"nir_band":3}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 29_evi_savi ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/29_evi_savi/run" \
  -F "file=@algorithms/29_evi_savi/testdata/input.tif" \
  -F 'params={"blue_band":0,"red_band":2,"nir_band":3}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 30_ndmi_ndwi ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/30_ndmi_ndwi/run" \
  -F "file=@algorithms/30_ndmi_ndwi/testdata/input.tif" \
  -F 'params={"green_band":1,"nir_band":3,"swir_band":5}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 31_red_edge_params ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/31_red_edge_params/run" \
  -F "file=@algorithms/31_red_edge_params/testdata/input.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 32_regression_inversion ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/32_regression_inversion/run" \
  -F "file=@algorithms/32_regression_inversion/testdata/input.tif" \
  -F "file2=@algorithms/32_regression_inversion/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 33_physical_inversion ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/33_physical_inversion/run" \
  -F "file=@algorithms/33_physical_inversion/testdata/input.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 34_svm_rf_classify ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/34_svm_rf_classify/run" \
  -F "file=@algorithms/34_svm_rf_classify/testdata/input.tif" \
  -F "file2=@algorithms/34_svm_rf_classify/testdata/file2.tif" \
  -F 'params={"test_size":0.3,"kernel":"rbf"}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 35_spectral_matching ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/35_spectral_matching/run" \
  -F "file=@algorithms/35_spectral_matching/testdata/input.tif" \
  -F "file2=@algorithms/35_spectral_matching/testdata/file2.csv" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 36_cnn1d_classify ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/36_cnn1d_classify/run" \
  -F "file=@algorithms/36_cnn1d_classify/testdata/input.tif" \
  -F "file2=@algorithms/36_cnn1d_classify/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 37_cnn3d_classify ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/37_cnn3d_classify/run" \
  -F "file=@algorithms/37_cnn3d_classify/testdata/input.tif" \
  -F "file2=@algorithms/37_cnn3d_classify/testdata/file2.tif" \
  -F 'params={"patch_size":5}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 38_transformer_classify ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/38_transformer_classify/run" \
  -F "file=@algorithms/38_transformer_classify/testdata/input.tif" \
  -F "file2=@algorithms/38_transformer_classify/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 39_few_shot_classify ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/39_few_shot_classify/run" \
  -F "file=@algorithms/39_few_shot_classify/testdata/input.tif" \
  -F "file2=@algorithms/39_few_shot_classify/testdata/file2.tif" \
  -F 'params={"shots":5}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 40_detect_segment ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/40_detect_segment/run" \
  -F "file=@algorithms/40_detect_segment/testdata/input.tif" \
  -F "file2=@algorithms/40_detect_segment/testdata/file2.geojson" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 41_unmixing ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/41_unmixing/run" \
  -F "file=@algorithms/41_unmixing/testdata/input.tif" \
  -F "file2=@algorithms/41_unmixing/testdata/file2.csv" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 42_anomaly_detect ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/42_anomaly_detect/run" \
  -F "file=@algorithms/42_anomaly_detect/testdata/input.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 43_change_detect ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/43_change_detect/run" \
  -F "file=@algorithms/43_change_detect/testdata/input.tif" \
  -F "file2=@algorithms/43_change_detect/testdata/file2.tif" \
  -F 'params={}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 44_postprocess_smooth ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/44_postprocess_smooth/run" \
  -F "file=@algorithms/44_postprocess_smooth/testdata/input.tif" \
  -F 'params={"min_pixels":4}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "=== 45_parcel_zonal_stats ==="
code=$(curl -s -o /tmp/algo_smoke.json -w "%{http_code}" -X POST "$HOST/api/v1/45_parcel_zonal_stats/run" \
  -F "file=@algorithms/45_parcel_zonal_stats/testdata/input.tif" \
  -F "file2=@algorithms/45_parcel_zonal_stats/testdata/file2.geojson" \
  -F 'params={"mode":"continuous","roi":[0,8,0,8]}')
if [[ "$code" == "200" ]]; then echo "OK http=$code"; pass=$((pass+1)); else echo "FAIL http=$code"; cat /tmp/algo_smoke.json; fail=$((fail+1)); fi

echo "----"
echo "pass=$pass fail=$fail skip=$skip"
[[ "$fail" -eq 0 ]]
