# Chart i18n plan (en/bn)

## Goal
- Allow authors to enter chart titles, column labels, metric labels per locale (en, bn) and render the matching locale at view time with sane fallbacks.

## Scope
- Explore/Dashboard chart titles.
- Dataset columns and metrics surfaced in controls/legends/tooltips.
- Import/export of charts and datasets.

## Storage model
- Chart params: keep `slice_name` as existing default; add `params.title_i18n` map.
- Columns/metrics: keep current `verbose_name`; add `extra.verbose_name_i18n` map.
- Fallback resolver: `i18n[currentLocale] || i18n.en || single-language field`.
- Example:
  ```json
  {
    "title_i18n": { "en": "Sales", "bn": "বিক্রয়" },
    "verbose_name_i18n": { "en": "Revenue", "bn": "রাজস্ব" }
  }
  ```

## Backend tasks
- Confirm `LANGUAGES` includes `en` and `bn`; ensure `BABEL_DEFAULT_LOCALE` set and language packs loaded.
- API: accept/return the i18n maps above on slice/dataset endpoints; validate JSON (keys are locales, values strings).
- Label resolver helper in backend for exports/imports to preserve maps; keep current fields untouched for backward compatibility.
- Tests: serialization/deserialization of i18n fields; import/export round-trip.

## Frontend tasks
- Global: ensure locale switch drives Redux `common.locale`.
- Inputs:
  - Chart title: show per-locale inputs (en, bn) with fallback notice; keep existing title field as default.
  - Dataset editor: add per-locale inputs for column/metric verbose names stored in `extra.verbose_name_i18n`.
- Rendering:
  - Central label resolver utility using fallback rule; use for chart title, control labels, tooltips, legends, table headers.
  - ECharts/other viz: pass resolved labels into options.
- UX: hide optional locale inputs unless a “Enable multilingual labels” toggle is on to reduce clutter.

## Testing & rollout
- Unit: resolver fallback logic; API schema validation.
- UI: form save/load for per-locale fields; locale switch shows correct labels in Explore and Dashboard.
- Regression: export/import with i18n fields preserved; charts still render when i18n maps missing.
- Docs: brief how-to for adding localized labels and required config to enable bn.
