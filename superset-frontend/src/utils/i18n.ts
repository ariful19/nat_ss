/**
 * i18n helpers for user-authored labels.
 */

type Translations = Record<string, string> | undefined | null;

export function resolveI18nLabel(
  translations: Translations,
  fallback: string | null | undefined,
  locale?: string | null,
): string | null | undefined {
  if (translations) {
    if (locale && translations[locale]) {
      return translations[locale];
    }
    if (translations.en) {
      return translations.en;
    }
  }
  return fallback;
}

export function normalizeI18nMap(
  value?: unknown,
): Record<string, string> | undefined {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return undefined;
  }

  const normalized: Record<string, string> = {};
  Object.entries(value as Record<string, unknown>).forEach(
    ([key, label]: [string, unknown]) => {
      if (typeof key === 'string' && typeof label === 'string') {
        normalized[key] = label;
      }
    },
  );
  return Object.keys(normalized).length ? normalized : undefined;
}
