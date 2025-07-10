'use client';

import '../i18n';
import { useTranslation } from 'react-i18next';
import Taskbar from './taskbar';
import { LanguageSwitcher } from './LanguageSwitcher';

export default function ClientHeader() {
  useTranslation();

  return (
    <header className="flex items-center justify-between px-4 py-3 shadow">
      <Taskbar />
      <LanguageSwitcher />
    </header>
  );
}
