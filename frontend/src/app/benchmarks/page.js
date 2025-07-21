'use client';

import '../i18n';
import { useTranslation } from 'react-i18next';
import Link from 'next/link';

export default function Benchmarks() {
  const { t } = useTranslation();

  return (
    // On ignore ici toute différence de rendu serveur/client dans ce div
    <div suppressHydrationWarning>
      <div className="max-w-3xl mx-auto px-2 py-3">
        <p className="text-1.5xl text-left text-gray-800">
          {t('benchmarksIntro')}
        </p>
      </div>
      <div className="space-y-8">
        <Benchmark
          title={t('benchmark_alloCine_title')}
          link="https://huggingface.co/datasets/CATIE-AQ/allocine_fr_prompt_sentiment_analysis"
          description={t('benchmark_alloCine_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_fquad_title')}
          link="https://arxiv.org/pdf/2002.06071"
          description={t('benchmark_fquad_description')}
          metrics="F1 Score, Exact Match Ratio"
        />
        <Benchmark
          title={t('benchmark_gqnli_title')}
          link="https://huggingface.co/datasets/maximoss/gqnli-fr"
          description={t('benchmark_gqnli_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_opusParcus_title')}
          link="https://huggingface.co/datasets/GEM/opusparcus"
          description={t('benchmark_opusParcus_description')}
          metrics="Pearson"
        />
        <Benchmark
          title={t('benchmark_paws_title')}
          link="https://github.com/google-research-datasets/paws"
          description={t('benchmark_paws_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_piaf_title')}
          link="https://aclanthology.org/2020.lrec-1.673/"
          description={t('benchmark_piaf_description')}
          metrics="F1 Score, Exact Match Ratio"
        />
        <Benchmark
          title={t('benchmark_qfrcola_title')}
          link="https://github.com/davebulaval/qfrcola"
          description={t('benchmark_qfrcola_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_qfrblimp_title')}
          link="https://github.com/davebulaval/FrBLiMP"
          description={t('benchmark_qfrblimp_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_sickfr_title')}
          link="https://huggingface.co/datasets/Lajavaness/SICK-fr"
          description={t('benchmark_sickfr_description')}
          metrics="Pearson"
        />
        <Benchmark
          title={t('benchmark_sts22_title')}
          link="https://huggingface.co/datasets/mteb/sts22-crosslingual-sts/viewer/fr"
          description={t('benchmark_sts22_description')}
          metrics="Pearson"
        />
        <Benchmark
          title={t('benchmark_xnli_title')}
          link="https://github.com/facebookresearch/XNLI"
          description={t('benchmark_xnli_description')}
          metrics="Accuracy"
        />
      </div>
    </div>
  );
}

function Benchmark({ title, description, metrics, link }) {
  const { t } = useTranslation();

  return (
    <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h3 className="text-xl font-semibold text-blue-700 mb-2 border-b-2 border-blue-500 inline-block">
        {link ? (
          <Link href={link} className="hover:underline">
            {title}
          </Link>
        ) : (
          title
        )}
      </h3>
      <p className="text-gray-700 mb-2">{description}</p>
      <p className="text-sm text-gray-500">
        <span className="font-medium">{t('metrics')}</span>: {metrics}
      </p>
    </div>
  );
}
