'use client';

import '../i18n';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ExternalLink, FileText, Menu, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useEffect, useRef, useState } from 'react';

const DATASETS_URL = 'https://huggingface.co/datasets/graalul/COLE-public';
const MENU_ID = 'primary-menu';

export default function Taskbar() {
  const { t } = useTranslation();
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  const navRef = useRef(null);
  const toggleRef = useRef(null);

  const closeMenu = () => setMenuOpen(false);

  // Close the mobile menu on Escape (returning focus to its button) and on
  // any pointer press outside the navigation.
  useEffect(() => {
    if (!menuOpen) return undefined;
    const onKeyDown = (e) => {
      if (e.key !== 'Escape') return;
      setMenuOpen(false);
      toggleRef.current?.focus();
    };
    const onPointerDown = (e) => {
      if (navRef.current && !navRef.current.contains(e.target)) setMenuOpen(false);
    };
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('pointerdown', onPointerDown);
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.removeEventListener('pointerdown', onPointerDown);
    };
  }, [menuOpen]);
  const isCurrent = (path) =>
    path === '/' ? pathname === '/' : pathname === path || pathname.startsWith(`${path}/`);

  const links = [
    { key: 'guide', href: '/guide', label: t('nav_guide'), match: '/guide' },
    { key: 'faq', href: '/FAQ', label: t('nav_faq'), match: '/FAQ' },
    { key: 'contact', href: '/contact', label: t('nav_contact'), match: '/contact' },
    { key: 'results', href: '/results', label: t('nav_results'), match: '/results' },
    { key: 'tasks', href: '/benchmarks', label: t('nav_tasks'), match: '/benchmarks' },
    { key: 'leaderboard', href: '/leaderboard', label: t('nav_leaderboard'), match: '/leaderboard' },
    { key: 'datasets', href: DATASETS_URL, label: t('nav_datasets'), external: true },
    { key: 'submit', href: `${pathname}?show=submit`, label: t('nav_submit'), primary: true },
  ];

  const renderLink = (link, layout) => {
    const current = link.match ? isCurrent(link.match) : false;
    const base = 'inline-flex min-h-11 items-center whitespace-nowrap rounded-md text-sm';
    let style;
    if (link.primary) {
      style = `${base} bg-accent px-4 font-semibold text-white hover:bg-accent-strong`;
    } else if (current) {
      style = `${base} px-2 font-semibold text-blue-700 underline decoration-2 underline-offset-8`;
    } else {
      style = `${base} px-2 text-gray-700 hover:text-blue-700`;
    }
    if (layout === 'mobile') style += ' w-full';

    const common = {
      className: style,
      onClick: closeMenu,
      'aria-current': current ? 'page' : undefined,
    };

    if (link.external) {
      return (
        <Link key={link.key} href={link.href} target="_blank" rel="noopener noreferrer" {...common}>
          {link.label}
          <ExternalLink className="ml-1 h-3.5 w-3.5" aria-hidden="true" />
          <span className="sr-only">{t('nav_newTab')}</span>
        </Link>
      );
    }
    return (
      <Link key={link.key} href={link.href} {...common}>
        {link.label}
      </Link>
    );
  };

  return (
    <nav ref={navRef} aria-label={t('nav_main')} className="min-w-0 flex-1 py-2">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center">
          <Link
            href="/"
            aria-current={pathname === '/' ? 'page' : undefined}
            className="inline-flex min-h-11 items-center rounded-md"
            onClick={closeMenu}
          >
            <span className="text-xl font-bold text-accent">{t('nav_home')}</span>
          </Link>
          <Link
            href="/papers"
            aria-label={t('nav_papers')}
            title={t('nav_papers')}
            aria-current={isCurrent('/papers') ? 'page' : undefined}
            className="ml-1 inline-flex h-11 w-11 items-center justify-center rounded-md"
            onClick={closeMenu}
          >
            <FileText className="h-6 w-6 text-accent hover:text-accent-strong" aria-hidden="true" />
          </Link>
        </div>

        {/* Desktop nav */}
        <div className="hidden items-center gap-x-3 xl:flex">
          {links.map((link) => renderLink(link, 'desktop'))}
        </div>

        {/* Mobile hamburger */}
        <button
          ref={toggleRef}
          data-menu-toggle
          type="button"
          className="inline-flex h-11 w-11 items-center justify-center rounded-md text-gray-700 xl:hidden"
          aria-label={menuOpen ? t('nav_menuClose') : t('nav_menuOpen')}
          aria-expanded={menuOpen}
          aria-controls={MENU_ID}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X className="h-6 w-6" aria-hidden="true" /> : <Menu className="h-6 w-6" aria-hidden="true" />}
        </button>
      </div>

      {/* Mobile menu */}
      <div
        id={MENU_ID}
        hidden={!menuOpen}
        className="mt-2 flex flex-col items-start gap-1 border-t border-gray-200 pt-2 xl:hidden"
      >
        {links.map((link) => renderLink(link, 'mobile'))}
      </div>
    </nav>
  );
}
