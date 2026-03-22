'use client';

import '../i18n';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FileText, Menu, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';

export default function Taskbar() {
  const { t } = useTranslation();
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  const linkStyle = (path) =>
    (pathname === path || (path !== '/' && pathname.startsWith(path)))
      ? 'text-blue-600 font-semibold border-b-2 border-blue-600 pb-1'
      : 'text-gray-700 hover:text-blue-500';

  const mobileLink = (path) =>
    (pathname === path || (path !== '/' && pathname.startsWith(path)))
      ? 'block text-blue-600 font-semibold py-2'
      : 'block text-gray-700 hover:text-blue-500 py-2';

  const links = (
    <>
      <Link href="/guide" className={linkStyle('/guide')} onClick={() => setMenuOpen(false)}>
        {t('nav_guide')}
      </Link>
      <Link href="/FAQ" className={linkStyle('/FAQ')} onClick={() => setMenuOpen(false)}>
        {t('nav_faq')}
      </Link>
      <Link href="/contact" className={linkStyle('/contact')} onClick={() => setMenuOpen(false)}>
        {t('nav_contact')}
      </Link>
      <Link href={`${pathname}?show=submit`} className={linkStyle('/submit')} onClick={() => setMenuOpen(false)}>
        {t('nav_submit')}
      </Link>
      <Link href="/results" className={linkStyle('/results')} onClick={() => setMenuOpen(false)}>
        {t('nav_results')}
      </Link>
      <Link href="/benchmarks" className={linkStyle('/benchmarks')} onClick={() => setMenuOpen(false)}>
        {t('nav_tasks')}
      </Link>
      <Link href="/leaderboard" className={linkStyle('/leaderboard')} onClick={() => setMenuOpen(false)}>
        {t('nav_leaderboard')}
      </Link>
      <Link href="https://huggingface.co/datasets/graalul/COLE-public" target="_blank" rel="noopener noreferrer" className={linkStyle('/hf')} onClick={() => setMenuOpen(false)}>
        {t('nav_datasets')}
      </Link>
    </>
  );

  const mobileLinks = (
    <>
      <Link href="/guide" className={mobileLink('/guide')} onClick={() => setMenuOpen(false)}>
        {t('nav_guide')}
      </Link>
      <Link href="/FAQ" className={mobileLink('/FAQ')} onClick={() => setMenuOpen(false)}>
        {t('nav_faq')}
      </Link>
      <Link href="/contact" className={mobileLink('/contact')} onClick={() => setMenuOpen(false)}>
        {t('nav_contact')}
      </Link>
      <Link href={`${pathname}?show=submit`} className={mobileLink('/submit')} onClick={() => setMenuOpen(false)}>
        {t('nav_submit')}
      </Link>
      <Link href="/results" className={mobileLink('/results')} onClick={() => setMenuOpen(false)}>
        {t('nav_results')}
      </Link>
      <Link href="/benchmarks" className={mobileLink('/benchmarks')} onClick={() => setMenuOpen(false)}>
        {t('nav_tasks')}
      </Link>
      <Link href="/leaderboard" className={mobileLink('/leaderboard')} onClick={() => setMenuOpen(false)}>
        {t('nav_leaderboard')}
      </Link>
      <Link href="https://huggingface.co/datasets/graalul/COLE-public" className={mobileLink('/hf')} onClick={() => setMenuOpen(false)}>
        {t('nav_datasets')}
      </Link>
    </>
  );

  return (
    <nav className="w-full py-4 mx-auto max-w-7xl px-4">
      <div className="flex justify-between items-center">
        <div className="flex items-center">
          <Link href="/">
            <span className="text-xl font-bold text-blue-600">{t('nav_home')}</span>
          </Link>
          <Link href="/papers" className="ml-2">
            <FileText className="w-6 h-6 text-blue-600 hover:text-blue-500" />
          </Link>
        </div>

        {/* Desktop nav */}
        <div className="hidden md:flex space-x-6">
          {links}
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden text-gray-700"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden mt-4 border-t border-gray-200 pt-4 space-y-1">
          {mobileLinks}
        </div>
      )}
    </nav>
  );
}
