'use client';

import '../i18n';
import {useTranslation, Trans} from 'react-i18next';
import Link from 'next/link';
import CodeBlock from '../components/CodeBlock';
import PageTitle, {SectionTitle} from '../components/PageTitle';

export default function Guide() {
    const {t} = useTranslation();

    return (
        <div className="max-w-[72ch] py-3">
            <PageTitle>{t('guide_title')}</PageTitle>

            <div className="space-y-8">
                {/* SECTION TRAINING & TESTING */}
                <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow transition">
                    <SectionTitle>{t('guide_section1_title')}</SectionTitle>

                    <p className="text-gray-700">
                        <Trans i18nKey="guide_section1_para1" components={[
                            <a key="hf-link"
                               href="https://huggingface.co/datasets/graalul/COLE-public"
                               target="_blank"
                               rel="noopener noreferrer"
                               className="text-blue-600 underline hover:text-blue-800"
                            />
                        ]}>
                        </Trans>
                    </p>

                    <p className="text-gray-700 mt-4">
                        <Trans i18nKey="guide_section1_para2" components={[<a key="github-ref"
                        href="https://github.com/GRAAL-Research/COLE"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 underline hover:text-blue-800">
                        GitHub Repository.
                        </a>]}> </Trans>

                    </p>

                    <p className="text-gray-700 mt-4">
                        <Trans i18nKey="guide_section1_para3">
                        </Trans>
                    </p>

                    {/* SECTION FORMATTING */}
                    <SectionTitle className="mt-8">{t('guide_section2_title')}</SectionTitle>
                    <p className="text-gray-700 mb-4">
                        {t('guide_section2_para1')}
                    </p>

                    <CodeBlock>{`{
  "model_name": "a_model_name",
  "model_url": "a_model_url",
  "tasks": [
    {
      "qfrcola": { "predictions": [1,1,1,1,1] }
    },
    {
      "allocine": { "predictions": [1,1,1,1,1] }
    }
  ]
}`}</CodeBlock>
                </div>
            </div>
        </div>
    );
}
