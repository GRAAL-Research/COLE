'use client';

import '../i18n'
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import PageTitle from '../components/PageTitle';

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

  // The navigation "Submit" button is the only primary action on the page.
  return (
    <div className="max-w-[72ch] py-3">
      <PageTitle>{t('results_default_title')}</PageTitle>
      <p className="text-gray-700">{t('results_default_message')}</p>
    </div>
  );
}
