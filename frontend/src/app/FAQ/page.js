'use client';

import '../i18n';
import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import PageTitle from '../components/PageTitle';

export default function FAQ() {
  const { t } = useTranslation();
  const faqs = t('faqs', { returnObjects: true });
  const [openIndex, setOpenIndex] = useState(null);

  const toggle = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="max-w-[72ch] py-3">
      <PageTitle>{t('faq_title')}</PageTitle>

      <div className="space-y-4">
        {faqs.map((faq, i) => {
          const isOpen = openIndex === i;
          return (
            <div
              key={i}
              className="rounded-lg border border-gray-200 bg-white shadow-sm"
            >
              <h2>
                <button
                  type="button"
                  id={`faq-question-${i}`}
                  aria-expanded={isOpen}
                  aria-controls={`faq-answer-${i}`}
                  className="flex min-h-11 w-full items-center justify-between gap-4 rounded-lg p-5 text-left text-lg font-semibold text-gray-900"
                  onClick={() => toggle(i)}
                >
                  <span>{`${i + 1}. ${faq.question}`}</span>
                  <ChevronDown
                    aria-hidden="true"
                    className={`h-5 w-5 shrink-0 text-gray-600 transition-transform motion-reduce:transition-none ${isOpen ? 'rotate-180' : ''}`}
                  />
                </button>
              </h2>
              <div
                id={`faq-answer-${i}`}
                role="region"
                aria-labelledby={`faq-question-${i}`}
                hidden={!isOpen}
                className="px-5 pb-5 text-gray-700"
              >
                {faq.answer.split(/(<code>.*?<\/code>)/g).map((part, j) =>
                  part.startsWith('<code>') ? (
                    <code key={j}>{part.replace(/<\/?code>/g, '')}</code>
                  ) : (
                    part
                  )
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
