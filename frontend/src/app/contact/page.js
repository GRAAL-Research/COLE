'use client';

import '../i18n';
import { useTranslation } from 'react-i18next';

export default function Contact() {
  const { t } = useTranslation();

  return (
    <div className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        {t('contact_title')}
      </h2>

      <p className="text-gray-700 mb-4 leading-relaxed">
        {t('contact_paragraph')}
      </p>

      <div className="bg-gray-50 p-4 rounded-md border border-dashed border-blue-400">
        <p className="text-sm text-gray-500 mb-2">
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
