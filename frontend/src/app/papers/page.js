'use client';

import React, { useState } from 'react';
import '../i18n';
import { ExternalLink } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import PageTitle from '../components/PageTitle';

const ARXIV_ABS = 'https://arxiv.org/abs/2510.05046';
const ARXIV_PDF = 'https://arxiv.org/pdf/2510.05046';

export default function PapersPage() {
  const [loaded, setLoaded] = useState(false);
  const { t } = useTranslation();

  return (
    <div className="flex h-[calc(100dvh-9rem)] min-h-[32rem] flex-col">
      <PageTitle className="mb-4">{t('papers_title')}</PageTitle>
      <div className="mb-4 space-y-1">
        <p>
          <a
            href={ARXIV_ABS}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-blue-700 underline hover:text-blue-900"
          >
            {t('papers_arxiv_label')}
          </a>
        </p>
        <p className="text-sm text-gray-700">{t('papers_arxiv_authors')}</p>
        <p>
          <a
            href={ARXIV_PDF}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex min-h-11 items-center gap-1 text-sm font-medium text-blue-700 underline hover:text-blue-900"
          >
            {t('papers_openPdf')}
            <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
          </a>
        </p>
      </div>

      <div className="relative min-h-0 flex-1 rounded-md border border-gray-200">
        {!loaded && (
          <div
            role="status"
            className="absolute inset-0 z-10 flex items-center justify-center bg-white"
          >
            <div
              className="h-12 w-12 animate-spin rounded-full border-4 border-accent border-t-transparent motion-reduce:animate-none"
              aria-hidden="true"
            />
            <span className="sr-only">{t('papers_loading')}</span>
          </div>
        )}
        <iframe
          onLoad={() => setLoaded(true)}
          src={ARXIV_PDF}
          title={t('papers_iframeTitle')}
          className="h-full w-full border-none"
        />
      </div>
    </div>
  );
}
