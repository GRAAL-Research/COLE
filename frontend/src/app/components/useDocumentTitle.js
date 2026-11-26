'use client';

import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export const TITLE_SUFFIX = ' | COLE';

// Keeps document.title in the visitor's language. Route layouts export static
// server metadata (the SSR and no-JS title); this overrides it once mounted and
// on every language or route change. Next.js can write its own title after
// hydration and after client navigations, so the head is watched and the
// localized title re-applied whenever it drifts.
export default function useDocumentTitle(key) {
  const { t, i18n } = useTranslation();
  const language = i18n.language;

  useEffect(() => {
    if (!key) return undefined;
    const wanted = `${t(`page_title_${key}`)}${TITLE_SUFFIX}`;
    const apply = () => {
      if (document.title !== wanted) document.title = wanted;
    };
    apply();
    const observer = new MutationObserver(apply);
    observer.observe(document.head, { childList: true, characterData: true, subtree: true });
    return () => observer.disconnect();
  }, [key, language, t]);
}
