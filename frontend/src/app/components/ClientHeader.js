'use client';

import { useEffect } from 'react';
import i18n, { detectLanguage } from '../i18n';
import { useTranslation } from 'react-i18next';
import Taskbar from './taskbar';
import { LanguageSwitcher } from './LanguageSwitcher';

export default function ClientHeader() {
  useTranslation();

  // The server and the first client render are English so hydration matches;
  // apply the visitor's language once mounted (this also updates <html lang>).
  useEffect(() => {
    const detected = detectLanguage();
    if (detected !== i18n.language) i18n.changeLanguage(detected);
  }, []);

  return (
    <header className="shadow">
      <div className="mx-auto flex w-full max-w-7xl items-start gap-4 px-4 sm:px-6">
        <Taskbar />
        <div className="py-2">
          <LanguageSwitcher />
        </div>
      </div>
    </header>
  );
}
