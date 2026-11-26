import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from "./en/translation.json";
import fr from './fr/translation.json';

const STORAGE_KEY = 'i18nextLng';

export const syncDocumentLanguage = (lng) => {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lng?.startsWith('fr') ? 'fr' : 'en';
  }
};

const toSupported = (lng) => (lng?.toLowerCase().startsWith('fr') ? 'fr' : 'en');

// Preferred language of the visitor: explicit choice first, then the browser.
// Client only; the server and the first client render always use English so
// that hydration matches.
export const detectLanguage = () => {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) return toSupported(stored);
  } catch {
    // Storage can be blocked; fall back to the browser language.
  }
  return toSupported(window.navigator.languages?.[0] ?? window.navigator.language);
};

// Explicit choice from the language switcher; remembered for the next visit.
export const setLanguage = (lng) => {
  try {
    window.localStorage.setItem(STORAGE_KEY, lng);
  } catch {
    // Ignore blocked storage; the choice still applies to this session.
  }
  return i18n.changeLanguage(lng);
};

i18n.on('languageChanged', syncDocumentLanguage);

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    fr: { translation: fr },
  },
  lng: 'en',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
