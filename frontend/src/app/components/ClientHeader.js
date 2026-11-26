'use client';

import { useEffect } from 'react';
import i18n, { detectLanguage } from '../i18n';
import { usePathname } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import Taskbar from './taskbar';
import { LanguageSwitcher } from './LanguageSwitcher';
import useDocumentTitle from './useDocumentTitle';

const TITLE_KEYS = ['guide', 'faq', 'contact', 'results', 'benchmarks', 'leaderboard', 'papers'];

// First path segment -> title key (page_title_<key>); the home page is "home".
const titleKeyFor = (pathname) => {
  const segment = (pathname.split('/')[1] ?? '').toLowerCase();
  if (segment === '') return 'home';
  return TITLE_KEYS.includes(segment) ? segment : null;
};

export default function ClientHeader() {
  useTranslation();
  useDocumentTitle(titleKeyFor(usePathname()));

  // The server and the first client render are English so hydration matches;
  // apply the visitor's language once mounted (this also updates <html lang>).
  useEffect(() => {
    const detected = detectLanguage();
    if (detected !== i18n.language) i18n.changeLanguage(detected);
  }, []);

  return (
    <header className="shadow">
      <div className="mx-auto flex w-full max-w-7xl items-start gap-4 px-4 sm:px-6">
        <Taskbar trailing={<LanguageSwitcher />} />
      </div>
    </header>
  );
}
