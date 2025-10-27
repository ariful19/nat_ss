# English/Bangla i18n feasibility in this Superset fork

Date: 2025-10-27

TL;DR
- Yes, platform i18n is built in (Flask-Babel backend + @superset-ui/core t() on frontend). Bangla (bn) is not bundled but can be added by providing a language pack and enabling it in config.
- Dual-language chart titles/labels aren’t first-class today, but can be implemented safely using existing JSON metadata fields and a small set of UI/resolve hooks so labels switch automatically with the selected locale.

What exists today (evidence from repo)
- Backend i18n
  - Babel config present in superset/config.py (BABEL_DEFAULT_LOCALE, BABEL_DEFAULT_FOLDER, LANGUAGES). The default LANGUAGES dict is defined, then overridden to {} (i18n disabled by default).
  - Translation packs structure under superset/translations/ with many locales and messages.pot. Runtime loader expects JSON packs at superset/translations/<locale>/LC_MESSAGES/messages.json (see superset/translations/utils.py).
- Frontend i18n
  - UI strings use t() from @superset-ui/core across the codebase (e.g., src/SqlLab, src/dashboard, etc.). This will pick up the active language pack without code changes once i18n is enabled.
- D3 locale hooks
  - D3_FORMAT config exists for number/currency grouping. Time locale can also be overridden; these are useful if Bangla-specific numerals/grouping are desired.

Enabling language switching + adding Bangla
1) Enable languages in config
   - In your superset_config.py, set (example):
     - BABEL_DEFAULT_LOCALE = "en"
     - BABEL_DEFAULT_FOLDER = "superset/translations"
     - LANGUAGES = { "en": {"flag": "us", "name": "English"}, "bn": {"flag": "bd", "name": "Bangla"} }
   - Note: upstream keeps LANGUAGES = {} to disable i18n by default; overriding in superset_config.py re-enables it.
2) Provide a Bangla language pack
   - Directory: superset/translations/bn/LC_MESSAGES/messages.json
   - File format must match other locales (JSON with domain superset); utils.py loads this directly. You can start with a minimal pack: only keys you care about; missing keys fall back to English.
   - How to create/update:
     - Extract keys with the existing babel.cfg and messages.pot under superset/translations, then translate and produce messages.json. If you don’t have the existing internal scripts, a practical path is to duplicate an existing locale’s messages.json and translate relevant keys incrementally.
3) Optional: Number/date localization
   - Configure D3_FORMAT and time locale for Bangla if you want Bangla numerals/grouping. Otherwise, keep Latin numerals and just translate UI strings.

Dual-language titles and labels during chart creation (design)
Goal: Allow authors to enter English and Bangla labels and have the UI auto-select based on current locale.

A) Storage (no DB migrations needed)
- Chart title: place i18n variants inside the chart’s params JSON, e.g. params.title_i18n = { "en": "Sales", "bn": "বিক্রয়" } while keeping slice_name as the default/fallback.
- Dataset columns: use the column’s extra/extra_json (or similar JSON field) to store verbose_name_i18n = { "en": "Revenue", "bn": "রাজস্ব" }.
- Metrics: similarly store metric.extra.verbose_name_i18n. These JSON “extra” fields are intended for metadata and survive exports/imports.

B) UI changes (small, isolated)
- Explore: For title/label inputs, add an optional “Bangla” field when a multilingual toggle is enabled. Persist to the i18n map described above.
- Dataset editor: Add optional “Bangla verbose name” for columns/metrics, persisting to extra.

C) Runtime label resolution (frontend-only)
- Determine active locale from bootstrap data (Superset exposes locale and language pack to the client) or @superset-ui/core utilities.
- Resolve display label as i18n[locale] || i18n["en"] || single-language field (slice_name/verbose_name). This ensures graceful fallback if a translation is missing.
- On language change, the same resolver re-renders labels automatically with the new locale.

D) Optional formatting
- If Bangla numerals/grouping are required, apply D3 locale overrides for format and time. Otherwise, keep default to avoid surprising users.

Limitations and considerations
- UI i18n vs. data labels: Core UI translations come from language packs; user-authored labels need to be stored per-object. The above approach keeps these concerns separate and safe.
- Search/sort: If the UI sorts by label, behavior will depend on locale/collation; this is usually acceptable for client-side lists.
- Exports/imports: JSON metadata fields are already included in Superset’s export/import; verify these keys in your pipeline.
- Governance: Decide whether multilingual inputs are optional or enforced; fallbacks ensure English displays when Bangla is missing.

Effort estimate (rough)
- Enable i18n + Bangla pack: 0.5–1.5 days depending on translation breadth.
- Dual-label UI (charts + dataset columns/metrics): 2–4 days for UI wiring, persistence, and resolver, plus QA.
- Optional D3 locale work: 0.5 day.

Summary
- Feasible with low risk: i18n infra already exists, and dual-language labels can ride on existing JSON metadata without schema changes. Start by enabling LANGUAGES and adding a bn messages.json, then add the minimal UI fields and a central label resolver to achieve automatic switching.
