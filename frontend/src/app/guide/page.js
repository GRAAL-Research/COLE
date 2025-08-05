'use client';

import '../i18n';
import {useTranslation, Trans} from 'react-i18next';
import Link from 'next/link';
import CodeBlock from '../components/CodeBlock';

export default function Guide() {
    const {t} = useTranslation();

    return (
        <div className="max-w-3xl mx-auto px-6 py-3">
            <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
                {t('guide_title')}
            </h2>

            <div className="space-y-8">
                {/* SECTION TRAINING & TESTING */}
                <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow transition">
                    <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-4">
                        {t('guide_section1_title')}
                    </h3>

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
                    <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-4">
                        {t('guide_section2_title')}
                    </h3>
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
