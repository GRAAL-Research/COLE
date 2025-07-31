'use client';

import '../i18n';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FileText } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function Taskbar() {
  const { t } = useTranslation();
  const pathname = usePathname();

  const linkStyle = (path) =>
    pathname === path
      ? 'text-blue-500 font-semibold'
      : 'text-gray-700 hover:text-blue-500';

  return (
    <nav className="w-full py-4 bg-none flex justify-between items-center mx-auto max-w-5xl">
      <div className="flex items-center">
        <Link href="/">
          <span className="text-xl font-bold text-blue-600">{t('nav_home')}</span>
        </Link>

        <Link href="/papers" className="ml-2">
          <FileText className="w-6 h-6 text-blue-600 hover:text-blue-500" />
        </Link>
      </div>

      <div className="space-x-6">
        <Link href="/guide" className={linkStyle('/guide')}>
          {t('nav_guide')}
        </Link>
        <Link href="/FAQ" className={linkStyle('/FAQ')}>
          {t('nav_faq')}
        </Link>
        <Link href="/contact" className={linkStyle('/contact')}>
          {t('nav_contact')}
        </Link>
        <Link
          href={`${pathname}?show=submit`}
          className={linkStyle('/submit')}
        >
          {t('nav_submit')}
        </Link>
        <Link href="/benchmarks" className={linkStyle('/benchmarks')}>
          {t('nav_tasks')}
        </Link>
        <Link href="/results" className={linkStyle('/results')}>
          {t('nav_results')}
        </Link>
        <Link href="/leaderboard" className={linkStyle('/leaderboard')}>
          {t('nav_leaderboard')}
        </Link>
        <Link
          href="https://huggingface.co/datasets/graalul/COLE-public"
          className={linkStyle('/hf')}
        >
          {t('nav_datasets')}
        </Link>
      </div>
    </nav>
  );
}
