'use client';

import '../i18n';
import { useTranslation } from 'react-i18next';
import Taskbar from './taskbar';
import { LanguageSwitcher } from './LanguageSwitcher';

export default function ClientHeader() {
  useTranslation();

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
