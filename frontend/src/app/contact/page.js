'use client';

import '../i18n';
import { useTranslation } from 'react-i18next';
import PageTitle from '../components/PageTitle';

export default function Contact() {
  const { t } = useTranslation();

  return (
    <div className="max-w-[72ch] py-3">
      <PageTitle>{t('contact_title')}</PageTitle>

      <p className="text-gray-700 mb-4 leading-relaxed">
        {t('contact_paragraph')}
      </p>

      <div className="bg-gray-50 p-4 rounded-md border border-dashed border-blue-400">
        <p className="text-sm text-gray-700 mb-2">
          {t('contact_email_label')}
        </p>
        <a
          href="mailto:david.beauchemin@ift.ulaval.ca"
          className="text-blue-600 font-mono text-lg hover:underline"
        >
          david.beauchemin@ift.ulaval.ca
        </a>
      </div>
    </div>
  );
}
