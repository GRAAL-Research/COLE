'use client';

import { useTranslation } from 'react-i18next';

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="flex space-x-2">
      <button onClick={() => changeLanguage('en')} className="px-2 py-1 rounded-lg border">
        EN
      </button>
      <button onClick={() => changeLanguage('fr')} className="px-2 py-1 rounded-lg border">
        FR
      </button>
    </div>
  );
}
