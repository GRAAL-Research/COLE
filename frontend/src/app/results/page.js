'use client';

import '../i18n'
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

export default function ResultsDefaultPage() {
  const router = useRouter();
  const { t } = useTranslation();

  useEffect(() => {
    const justSubmitted = localStorage.getItem('just_submitted');
    const savedFile = localStorage.getItem('last_result_file');

    if (justSubmitted && savedFile) {
      const id = savedFile.replace('.json', '');
      localStorage.removeItem('just_submitted');
      router.push(`/results/${id}`);
    }
  }, [router]);

  return (
    <main className="max-w-2xl mx-auto px-6 py-12 text-center">
      <h1 className="text-3xl font-bold text-blue-700 mb-4">
        {t('results_default_title')}
      </h1>
      <p className="text-gray-700">{t('results_default_message')}</p>
    </main>
  );
}
