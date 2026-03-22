'use client';

import '../i18n';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export default function FAQ() {
  const { t } = useTranslation();
  const faqs = t('faqs', { returnObjects: true });
  const [openIndex, setOpenIndex] = useState(null);

  const toggle = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        {t('faq_title')}
      </h2>

      <div className="space-y-4">
        {faqs.map((faq, i) => (
          <div
            key={i}
            className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm transition"
          >
            <button
              className="w-full text-left text-xl font-semibold text-gray-800 flex justify-between items-center"
              onClick={() => toggle(i)}
            >
              <span>{`${i + 1}. ${faq.question}`}</span>
              <span className="text-2xl text-gray-500">
                {openIndex === i ? '▴' : '▾'}
              </span>
            </button>
            {openIndex === i && (
              <p className="mt-4 text-gray-600 text-sm">
                {faq.answer.split(/(<code>.*?<\/code>)/g).map((part, j) =>
                  part.startsWith('<code>') ? (
                    <code key={j}>{part.replace(/<\/?code>/g, '')}</code>
                  ) : (
                    part
                  )
                )}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
