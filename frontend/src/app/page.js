'use client'

import Link from "next/link";
import { Trans } from 'react-i18next';
import { useTranslation } from 'react-i18next';

export default function Home() {
  const { t } = useTranslation();

  return (
    <div className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        {t('home_whatIsColleTitle')}
      </h2>

      <p className="text-gray-700 mb-4 leading-relaxed space-y-4">
        <Trans i18nKey="home_paragraph1">
          COLE is a multidisciplinary French Natural Language Understanding benchmark (
          <a
            href="https://en.wikipedia.org/wiki/Natural_language_understanding"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline hover:text-blue-800"
          >
            NLU
          </a>
          ). It takes inspiration from its predecessors&nbsp;
          <a
            href="https://gluebenchmark.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline hover:text-blue-800"
          >
            GLUE
          </a>
          &nbsp;and&nbsp;
          <a
            href="https://super.gluebenchmark.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline hover:text-blue-800"
          >
            SuperGLUE
          </a>
          &nbsp;to build a benchmark capable of evaluating models in the French language on multiple topics of language understanding. See&nbsp;
          <Link
            href="/404"
            className="text-blue-600 underline hover:text-blue-800"
          >
            our paper
          </Link>
          &nbsp;for more information.
        </Trans>
      </p>

      <p className="text-gray-700 leading-relaxed">
        {t('home_paragraph2')}
      </p>

      <p className="text-gray-700 leading-relaxed mt-4">
        <Trans i18nKey="home_paragraph3">
          We have made the choice to hide test labels to discourage cheating or overfitting on test data. To get results on your test data, you may send us your results as explained in&nbsp;
          <Link
            href="/guide"
            className="text-blue-600 underline hover:text-blue-800"
          >
            our guide
          </Link>
          .
        </Trans>
      </p>
    </div>
  );
}
