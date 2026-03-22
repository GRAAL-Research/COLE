'use client';

import React, { useState } from 'react';
import '../i18n';
import { useTranslation } from 'react-i18next';

export default function PapersPage() {
  const [loaded, setLoaded] = useState(false);
  const { t } = useTranslation();

  return (
    <div className="relative h-screen">
      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-white z-10">
          <div className="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full" />
        </div>
      )}
      <div className="max-w-5xl mx-auto px-6 py-3">
        <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-6">
          {t('papers_title')}
        </h2>
        <div className="mb-6 space-y-2">
          <p className="text-gray-700">
            <a
              href="https://arxiv.org/abs/2510.05046"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 underline hover:text-blue-800 font-medium"
            >
              {t('papers_arxiv_label')}
            </a>
            {' '}&mdash; {t('papers_arxiv_authors')}
          </p>
        </div>
      </div>

      <iframe
        onLoad={() => setLoaded(true)}
        src="cole.pdf"
        title="Document COLE"
        width="100%"
        height="100%"
        className="border-none"
      />
    </div>
  );
}
