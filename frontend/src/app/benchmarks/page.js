'use client';

import '../i18n';
import { useTranslation } from 'react-i18next';
import Link from 'next/link';

export default function Benchmarks() {
  const { t } = useTranslation();

  return (
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
          title={t('benchmark_daccord_title')}
          link="https://huggingface.co/datasets/maximoss/daccord-contradictions"
          description={t('benchmark_daccord_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_fquad_title')}
          link="https://arxiv.org/pdf/2002.06071"
          description={t('benchmark_fquad_description')}
          metrics="F1 Score, Exact Match Ratio"
        />
        <Benchmark
          title={t('benchmark_french_boolq_title')}
          link="https://huggingface.co/datasets/manu/french_boolq"
          description={t('benchmark_french_boolq_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_fracas_title')}
          link="https://huggingface.co/datasets/maximoss/fracas"
          description={t('benchmark_fracas_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_gqnli_title')}
          link="https://huggingface.co/datasets/maximoss/gqnli-fr"
          description={t('benchmark_gqnli_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_lingnli_title')}
          link="https://huggingface.co/datasets/maximoss/lingnli-multi-mt"
          description={t('benchmark_lingnli_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_mms_title')}
          link="https://huggingface.co/datasets/Brand24/mms"
          description={t('benchmark_mms_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_mnli_nineeleven_fr_mt_title')}
          link="https://huggingface.co/datasets/maximoss/mnli-nineeleven-fr-mt"
          description={t('benchmark_mnli_nineeleven_fr_mt_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_multiblimp_title')}
          link="https://huggingface.co/datasets/jumelet/multiblimp"
          description={t('benchmark_multiblimp_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_paws_title')}
          link="https://huggingface.co/datasets/google-research-datasets/paws-x"
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
          title={t('benchmark_qfrblimp_title')}
          link="https://github.com/davebulaval/FrBLiMP"
          description={t('benchmark_qfrblimp_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_qfrcola_title')}
          link="https://github.com/davebulaval/qfrcola"
          description={t('benchmark_qfrcola_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_qfrcore_title')}
          link=""
          description={t('benchmark_qfrcore_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_qfrcort_title')}
          link=""
          description={t('benchmark_qfrcort_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_rte3_french_title')}
          link="https://huggingface.co/datasets/maximoss/rte3-french"
          description={t('benchmark_rte3_french_description')}
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
          title={t('benchmark_wino_x_lm_title')}
          link="https://huggingface.co/datasets/demelin/wino_x/viewer/lm_en_fr?views%5B%5D=lm_en_fr"
          description={t('benchmark_wino_x_lm_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_wino_x_mt_title')}
          link="https://huggingface.co/datasets/demelin/wino_x/viewer/mt_en_fr"
          description={t('benchmark_wino_x_mt_description')}
          metrics="Accuracy"
        />
        <Benchmark
          title={t('benchmark_wsd_title')}
          link="https://huggingface.co/datasets/GETALP/flue"
          description={t('benchmark_wsd_description')}
          metrics="Exact Match Ratio"
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
        <span className="font-medium">{t('metrics')}</span> {metrics}
      </p>
    </div>
  );
}
