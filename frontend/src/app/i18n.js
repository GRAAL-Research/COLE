import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from "./en/translation.json";
import fr from './fr/translation.json';

export const syncDocumentLanguage = (lng) => {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lng?.startsWith('fr') ? 'fr' : 'en';
  }
};

i18n.on('languageChanged', syncDocumentLanguage);

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      fr: { translation: fr },
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  })
  .then(() => syncDocumentLanguage(i18n.language));

export default i18n;
